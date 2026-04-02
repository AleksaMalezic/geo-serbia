import pytest

from src.domains.locations.models import Location


async def login_with_cookie(client, username: str, password: str):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("success") is True


@pytest.mark.asyncio
async def test_game_start_adaptive_returns_rounds(client, user):
    for idx in range(7):
        await Location.create(
            name=f"Adaptive {idx}",
            description="seed",
            latitude=44.0 + idx * 0.01,
            longitude=20.0 + idx * 0.01,
            created_by=user,
            is_approved=True,
        )

    await login_with_cookie(client, "testuser", "Password123!")

    resp = await client.post("/api/v1/game/start", params={"mode": "adaptive"})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("success") is True
    payload = body.get("data", {})
    assert payload.get("mode") == "adaptive"
    assert len(payload.get("rounds", [])) == 5
    assert payload.get("difficulty_tier") in {"easy", "normal", "hard"}


@pytest.mark.asyncio
async def test_profile_adaptive_stats_endpoint(client, user, approved_location):
    await login_with_cookie(client, "testuser", "Password123!")

    play_resp = await client.post(
        "/api/v1/game/play",
        params={
            "location_id": approved_location.id,
            "guessed_latitude": 45.1,
            "guessed_longitude": 20.1,
        },
    )
    assert play_resp.status_code == 200

    stats_resp = await client.get("/api/v1/profile/adaptive-stats")
    assert stats_resp.status_code == 200
    body = stats_resp.json()
    payload = body.get("data", {})
    assert "current_skill_rating" in payload
    assert "difficulty_tier" in payload
    assert "recent_improvement_percent" in payload


@pytest.mark.asyncio
async def test_admin_adaptive_stats_endpoint(client, admin_user):
    await login_with_cookie(client, "admin", "AdminPass123!")

    resp = await client.get("/api/v1/admin/adaptive/stats")
    assert resp.status_code == 200
    body = resp.json()
    payload = body.get("data", {})
    assert "tier_distribution" in payload
    assert "fallback_rate" in payload
    assert "top_unstable_locations" in payload
