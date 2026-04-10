from datetime import datetime
from bisect import bisect_right
from random import shuffle, uniform

from fastapi import HTTPException
from tortoise.functions import Max

from src.domains.games.models import (
    AdaptiveDecisionLog,
    GameSession,
    LocationDifficultyProfile,
    Round,
    UserSkillProfile,
)
from src.domains.locations.models import Location
from src.domains.users.models import User

MAX_RECENT_ROUNDS = 10
MAX_DAILY_ROUNDS = 5
HINT_PENALTIES = [0.08, 0.12, 0.20]
RANK_DISTRIBUTION = [
    ("bronze", 0.20),
    ("silver", 0.50),
    ("gold", 0.70),
    ("platinum", 0.85),
    ("diamond", 0.95),
    ("champion", 1.00),
]


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _difficulty_tier(score: float) -> str:
    if score < 40:
        return "easy"
    if score > 66:
        return "hard"
    return "normal"


def _rank_from_percentile(percentile: float) -> str:
    p = _clamp(percentile, 0.0, 1.0)
    for name, threshold in RANK_DISTRIBUTION:
        if p <= threshold:
            return name
    return "champion"


def _percentile_from_sorted(skills: list[float], skill_rating: float) -> float:
    if not skills:
        return 0.5
    position = bisect_right(skills, float(skill_rating))
    return position / len(skills)


def _normalize_hints(raw_hints) -> list[str]:
    if not raw_hints or not isinstance(raw_hints, list):
        return []
    cleaned = []
    for item in raw_hints:
        if isinstance(item, str) and item.strip():
            cleaned.append(item.strip())
    return cleaned[:3]


def _hint_penalty(hints_used_count: int) -> float:
    used = max(0, min(hints_used_count, len(HINT_PENALTIES)))
    return sum(HINT_PENALTIES[:used])


async def get_or_create_daily_session(user_id: int) -> GameSession:
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    session = await GameSession.filter(user_id=user_id, created_at__gte=today_start).first()
    if session:
        return session
    return await GameSession.create(user_id=user_id)


async def get_or_create_user_skill_profile(user_id: int) -> UserSkillProfile:
    profile = await UserSkillProfile.filter(user_id=user_id).first()
    if profile:
        return profile
    return await UserSkillProfile.create(user_id=user_id, skill_rating=52)


async def get_or_create_location_difficulty_profile(location_id: int) -> LocationDifficultyProfile:
    profile = await LocationDifficultyProfile.filter(location_id=location_id).first()
    if profile:
        return profile
    return await LocationDifficultyProfile.create(location_id=location_id, difficulty_rating=50)


async def _recent_location_ids(user_id: int, limit: int = 40) -> set[int]:
    recent_rounds = (
        await Round.filter(session__user_id=user_id)
        .order_by("-created_at")
        .limit(limit)
        .all()
    )
    return {int(r.location_id) for r in recent_rounds if r.location_id is not None}


async def _get_rank_snapshot(skill_rating: float) -> tuple[str, float]:
    profiles = await UserSkillProfile.all().only("skill_rating")
    sorted_skills = sorted(float(p.skill_rating or 52) for p in profiles)
    percentile = _percentile_from_sorted(sorted_skills, float(skill_rating))
    return _rank_from_percentile(percentile), percentile


def _select_adaptive_locations(enriched: list[dict], target: float, rounds: int, recent_ids: set[int]) -> tuple[list[dict], bool]:
    if not enriched:
        return [], True

    noisy_target = _clamp(target + uniform(-12.0, 12.0), 0.0, 100.0)
    windows = (14.0, 24.0, 100.0)
    pool = []
    fallback_used = False
    for idx, window in enumerate(windows):
        pool = [row for row in enriched if abs(row["difficulty_rating"] - noisy_target) <= window]
        if len(pool) >= rounds or idx == len(windows) - 1:
            fallback_used = idx > 0
            break

    shuffle(pool)
    pool.sort(
        key=lambda row: (
            row["location"].id in recent_ids,
            abs(row["difficulty_rating"] - noisy_target),
        )
    )

    selected = pool[:rounds]
    if len(selected) < rounds:
        selected_ids = {row["location"].id for row in selected}
        remaining = [row for row in enriched if row["location"].id not in selected_ids]
        shuffle(remaining)
        remaining.sort(
            key=lambda row: (
                row["location"].id in recent_ids,
                abs(row["difficulty_rating"] - noisy_target),
            )
        )
        selected.extend(remaining[: rounds - len(selected)])
        fallback_used = True

    return selected[:rounds], fallback_used


async def get_hint(user_id: int, location_id: int, hints_used_count: int):
    _ = await get_or_create_daily_session(user_id)
    location = await Location.get_or_none(id=location_id, is_approved=True)
    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronadjena.")

    hints = _normalize_hints(location.hints)
    if not hints:
        raise HTTPException(status_code=400, detail="No hints available for this location.")

    used = max(0, hints_used_count)
    if used >= len(hints):
        raise HTTPException(status_code=400, detail="All hints already used.")

    next_count = used + 1
    return {
        "hint_index": next_count,
        "hint_text": hints[used],
        "hints_used_count": next_count,
        "max_hints": len(hints),
        "current_penalty_percent": round(_hint_penalty(next_count) * 100, 2),
    }


async def start_challenge(user_id: int, mode: str = "adaptive", rounds: int = MAX_DAILY_ROUNDS):
    mode = "adaptive"
    user_profile = await get_or_create_user_skill_profile(user_id)
    session = await get_or_create_daily_session(user_id)

    approved = await Location.filter(is_approved=True).all()
    if len(approved) < rounds:
        raise HTTPException(status_code=400, detail="Not enough approved locations.")

    enriched = []
    for location in approved:
        difficulty = await get_or_create_location_difficulty_profile(location.id)
        enriched.append(
            {
                "location": location,
                "difficulty_rating": float(difficulty.difficulty_rating or 50),
            }
        )

    target = float(user_profile.skill_rating or 52)
    recent_ids = await _recent_location_ids(user_id=user_id, limit=40)
    selected, fallback_used = _select_adaptive_locations(enriched, target=target, rounds=rounds, recent_ids=recent_ids)
    rank_tier, rank_percentile = await _get_rank_snapshot(target)

    await AdaptiveDecisionLog.create(
        user_id=user_id,
        mode=mode,
        chosen_band=rank_tier,
        fallback_used=fallback_used,
        candidate_pool_size=len(approved),
    )

    response_rounds = []
    for row in selected:
        loc = row["location"]
        hints = _normalize_hints(loc.hints)
        response_rounds.append(
            {
                "id": loc.id,
                "name": loc.name,
                "description": loc.description,
                "image_url": loc.image_url,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "difficulty": _difficulty_tier(row["difficulty_rating"]),
                "difficulty_rating": round(float(row["difficulty_rating"]), 2),
                "max_hints": len(hints),
            }
        )

    return {
        "session_id": session.id,
        "mode": mode,
        "difficulty_tier": _difficulty_tier(float(user_profile.skill_rating or 52)),
        "skill_rating": round(float(user_profile.skill_rating or 52), 2),
        "rank_tier": rank_tier,
        "rank_percentile": round(rank_percentile * 100, 2),
        "rounds": response_rounds,
    }


async def _update_profiles_after_round(
    user_id: int,
    location_id: int,
    round_score: float,
    distance_km: float,
):
    profile = await get_or_create_user_skill_profile(user_id)
    before_skill = float(profile.skill_rating or 52)
    rank_tier_before, _ = await _get_rank_snapshot(before_skill)

    recent_rounds = (
        await Round.filter(session__user_id=user_id)
        .order_by("-created_at")
        .limit(MAX_RECENT_ROUNDS)
        .all()
    )
    scores = [float(r.score) for r in recent_rounds]
    distances = [float(r.distance_km) for r in recent_rounds]
    if not scores:
        scores = [float(round_score)]
    if not distances:
        distances = [float(distance_km)]

    avg_points = sum(scores) / len(scores)
    avg_distance = sum(distances) / len(distances)

    variance = 0.0
    if len(scores) > 1:
        variance = sum((s - avg_points) ** 2 for s in scores) / len(scores)
    consistency = _clamp(1 - (variance**0.5) / 250.0, 0, 1)

    raw_skill = (avg_points / 5000.0) * 70 + _clamp(1 - (avg_distance / 250.0), 0, 1) * 30
    profile.skill_rating = _clamp(raw_skill * 100, 0, 100)
    profile.recent_avg_points = avg_points
    profile.recent_avg_distance_km = avg_distance
    profile.consistency_index = consistency
    await profile.save()

    location_profile = await get_or_create_location_difficulty_profile(location_id)
    attempts = int(location_profile.attempt_count or 0) + 1
    location_profile.global_avg_distance_km = (
        (float(location_profile.global_avg_distance_km or 0) * (attempts - 1) + float(distance_km)) / attempts
    )
    location_profile.global_avg_points = (
        (float(location_profile.global_avg_points or 0) * (attempts - 1) + float(round_score)) / attempts
    )
    location_profile.attempt_count = attempts
    location_profile.difficulty_rating = _clamp(
        (location_profile.global_avg_distance_km / 250.0) * 70
        + _clamp(1 - (location_profile.global_avg_points / 5000.0), 0, 1) * 30,
        0,
        100,
    )
    await location_profile.save()

    after_skill = float(profile.skill_rating or before_skill)
    rank_tier_after, _ = await _get_rank_snapshot(after_skill)
    return (
        before_skill,
        after_skill,
        _difficulty_tier(after_skill),
        rank_tier_before,
        rank_tier_after,
    )


async def play_round(user_id: int, location_id: int, guessed_lat: float, guessed_lon: float, hints_used_count: int = 0):
    session = await get_or_create_daily_session(user_id)

    rounds_today = await Round.filter(session=session).count()
    if rounds_today >= MAX_DAILY_ROUNDS:
        raise HTTPException(status_code=400, detail="Danas ste vec odigrali maksimalan broj rundi.")

    location = await Location.get_or_none(id=location_id, is_approved=True)
    if not location:
        raise HTTPException(status_code=404, detail="Lokacija nije pronadjena.")

    distance = Round.calculate_distance(guessed_lat, guessed_lon, location.latitude, location.longitude)
    base_score = Round.calculate_score(distance)

    max_hints = len(_normalize_hints(location.hints))
    applied_hints = max(0, min(hints_used_count, max_hints))
    penalty = _hint_penalty(applied_hints)
    score = max(0.0, base_score * (1 - penalty))

    skill_before, skill_after, difficulty_used, rank_tier_before, rank_tier_after = await _update_profiles_after_round(
        user_id=user_id,
        location_id=location.id,
        round_score=score,
        distance_km=distance,
    )

    new_round = await Round.create(
        session=session,
        location=location,
        guessed_latitude=guessed_lat,
        guessed_longitude=guessed_lon,
        distance_km=distance,
        base_score=base_score,
        hint_penalty_percent=penalty * 100,
        hints_used_count=applied_hints,
        score=score,
    )

    session.total_score += score
    session.rounds_played += 1
    await session.save()

    return {
        "round_id": new_round.id,
        "location": location.id,
        "distance_km": round(distance, 2),
        "base_score": int(base_score),
        "hint_penalty_percent": round(penalty * 100, 2),
        "hints_used_count": applied_hints,
        "score": int(score),
        "total_score": int(session.total_score),
        "rounds_played": int(session.rounds_played),
        "difficulty_used": difficulty_used,
        "skill_rating_before": round(skill_before, 2),
        "skill_rating_after": round(skill_after, 2),
        "rank_tier_before": rank_tier_before,
        "rank_tier_after": rank_tier_after,
    }


async def get_daily_leaderboard():
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    sessions = (
        await GameSession.filter(created_at__gte=today_start)
        .order_by("-total_score")
        .limit(10)
        .prefetch_related("user")
    )

    results = []
    for s in sessions:
        results.append(
            {
                "username": s.user.username,
                "total_score": int(s.total_score),
                "rounds_played": int(s.rounds_played),
                "date": s.created_at.date(),
            }
        )
    return results


async def get_monthly_leaderboard():
    today = datetime.utcnow()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    best_sessions = (
        await GameSession.filter(created_at__gte=month_start)
        .group_by("user_id")
        .annotate(best_score=Max("total_score"))
        .order_by("-best_score")
        .limit(10)
    )

    results = []
    for s in best_sessions:
        user = await User.get(id=s.user_id)
        results.append(
            {
                "username": user.username,
                "total_points": int(s.best_score or 0),
            }
        )
    return results


async def get_user_adaptive_stats(user_id: int):
    profile = await get_or_create_user_skill_profile(user_id)
    recent_rounds = (
        await Round.filter(session__user_id=user_id)
        .order_by("-created_at")
        .limit(MAX_RECENT_ROUNDS)
        .all()
    )

    if not recent_rounds:
        improvement = 0.0
    else:
        points = [float(r.score) for r in reversed(recent_rounds)]
        midpoint = len(points) // 2
        before = points[:midpoint] if midpoint else points
        after = points[midpoint:] if midpoint else points
        before_avg = (sum(before) / len(before)) if before else 0
        after_avg = (sum(after) / len(after)) if after else 0
        improvement = ((after_avg - before_avg) / before_avg) * 100 if before_avg > 0 else 0

    current_skill = float(profile.skill_rating or 52)
    rank_tier, rank_percentile = await _get_rank_snapshot(current_skill)

    return {
        "current_skill_rating": round(current_skill, 2),
        "difficulty_tier": _difficulty_tier(current_skill),
        "rank_tier": rank_tier,
        "rank_percentile": round(rank_percentile * 100, 2),
        "recent_improvement_percent": round(improvement, 2),
        "recent_avg_distance_km": round(float(profile.recent_avg_distance_km or 0), 2),
        "recent_avg_points": round(float(profile.recent_avg_points or 0), 2),
        "consistency_index": round(float(profile.consistency_index or 0), 2),
    }


async def get_admin_adaptive_stats():
    profiles = await UserSkillProfile.all()
    sorted_skills = sorted(float(p.skill_rating or 52) for p in profiles)

    easy = 0
    normal = 0
    hard = 0
    rank_distribution = {name: 0 for name, _ in RANK_DISTRIBUTION}
    for p in profiles:
        skill = float(p.skill_rating or 52)
        tier = _difficulty_tier(skill)
        if tier == "easy":
            easy += 1
        elif tier == "hard":
            hard += 1
        else:
            normal += 1
        percentile = _percentile_from_sorted(sorted_skills, skill)
        rank_distribution[_rank_from_percentile(percentile)] += 1

    decision_count = await AdaptiveDecisionLog.all().count()
    fallback_count = await AdaptiveDecisionLog.filter(fallback_used=True).count()
    fallback_rate = (fallback_count / decision_count) * 100 if decision_count else 0

    unstable_profiles = (
        await LocationDifficultyProfile.all().order_by("-difficulty_rating").limit(10).prefetch_related("location")
    )
    unstable = []
    for p in unstable_profiles:
        unstable.append(
            {
                "location_id": p.location_id,
                "name": p.location.name if p.location else None,
                "variance": round(float(p.difficulty_rating or 0), 2),
            }
        )

    return {
        "tier_distribution": {
            "easy": easy,
            "normal": normal,
            "hard": hard,
        },
        "rank_distribution": rank_distribution,
        "fallback_rate": round(fallback_rate, 2),
        "top_unstable_locations": unstable,
    }