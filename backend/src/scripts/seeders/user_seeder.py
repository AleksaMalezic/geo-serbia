from src.domains.games.models import UserSkillProfile
from src.domains.users.models import User
from src.domains.users.services import hash_password


USERS = [
    {
        "username": "geo_admin",
        "email": "admin@geo.rs",
        "password": "admin123",
        "is_admin": True,
    },
    {
        "username": "geo_user",
        "email": "user@geo.rs",
        "password": "user123",
        "is_admin": False,
    },
    {
        "username": "maleza",
        "email": "maleza@geo.rs",
        "password": "sifra123",
        "is_admin": False,
    },
    {
        "username": "tojaga",
        "email": "tojaga@geo.rs",
        "password": "sifra123",
        "is_admin": False,
    },
    {
        "username": "somi",
        "email": "somi@geo.rs",
        "password": "sifra123",
        "is_admin": False,
    },
]


# Persona skill presets used by adaptive mode.
# - tojaga: struggling player (easy tier)
# - somi: average player (normal tier)
# - maleza: strong player (hard tier)
USER_SKILL_PRESETS = {
    "tojaga": {
        "skill_rating": 28.0,
        "recent_avg_distance_km": 170.0,
        "recent_avg_points": 850.0,
        "consistency_index": 0.35,
    },
    "somi": {
        "skill_rating": 54.0,
        "recent_avg_distance_km": 70.0,
        "recent_avg_points": 2300.0,
        "consistency_index": 0.62,
    },
    "maleza": {
        "skill_rating": 84.0,
        "recent_avg_distance_km": 14.0,
        "recent_avg_points": 4300.0,
        "consistency_index": 0.88,
    },
}


async def _upsert_user(user_data: dict) -> User:
    existing = await User.filter(username=user_data["username"]).first()
    if existing:
        changed = False
        if existing.email != user_data["email"]:
            existing.email = user_data["email"]
            changed = True
        if existing.is_admin != user_data["is_admin"]:
            existing.is_admin = user_data["is_admin"]
            changed = True
        if changed:
            await existing.save()
        return existing

    return await User.create(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hash_password(user_data["password"]),
        is_admin=user_data["is_admin"],
        is_active=True,
    )


async def _upsert_skill_profile(user: User):
    preset = USER_SKILL_PRESETS.get(user.username)
    if not preset:
        return

    profile = await UserSkillProfile.filter(user_id=user.id).first()
    if not profile:
        await UserSkillProfile.create(user_id=user.id, **preset)
        return

    profile.skill_rating = preset["skill_rating"]
    profile.recent_avg_distance_km = preset["recent_avg_distance_km"]
    profile.recent_avg_points = preset["recent_avg_points"]
    profile.consistency_index = preset["consistency_index"]
    await profile.save()


async def seed():
    created_count = 0
    for u in USERS:
        existing_before = await User.filter(username=u["username"]).exists()
        user = await _upsert_user(u)
        if not existing_before:
            created_count += 1
        await _upsert_skill_profile(user)

    print(f"Users seeded. Created: {created_count}")
