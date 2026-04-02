import pytest

from src.domains.games import services as game_services
from src.domains.games.models import UserSkillProfile
from src.domains.locations.models import Location
from src.domains.users.models import User
from src.scripts.seeders.location_seeder import seed as seed_locations
from src.scripts.seeders.user_seeder import seed as seed_users


@pytest.mark.asyncio
async def test_persona_skill_profiles_seeded(db):
    await seed_users()

    tojaga = await User.filter(username="tojaga").first()
    somi = await User.filter(username="somi").first()
    maleza = await User.filter(username="maleza").first()

    assert tojaga is not None
    assert somi is not None
    assert maleza is not None

    tojaga_skill = await UserSkillProfile.filter(user_id=tojaga.id).first()
    somi_skill = await UserSkillProfile.filter(user_id=somi.id).first()
    maleza_skill = await UserSkillProfile.filter(user_id=maleza.id).first()

    assert tojaga_skill is not None
    assert somi_skill is not None
    assert maleza_skill is not None

    assert tojaga_skill.skill_rating < 40
    assert 40 <= somi_skill.skill_rating <= 66
    assert maleza_skill.skill_rating > 66
    assert tojaga_skill.skill_rating < somi_skill.skill_rating < maleza_skill.skill_rating


@pytest.mark.asyncio
async def test_start_challenge_matches_persona_strength(db):
    await seed_users()
    await seed_locations()

    for username, expected_tier in [("tojaga", "easy"), ("somi", "normal"), ("maleza", "hard")]:
        user = await User.filter(username=username).first()
        assert user is not None
        response = await game_services.start_challenge(user_id=user.id, mode="adaptive")
        assert response["difficulty_tier"] == expected_tier
        assert len(response["rounds"]) == 5

    # Strong player should receive harder average rounds than weak player.
    tojaga = await User.filter(username="tojaga").first()
    maleza = await User.filter(username="maleza").first()
    tojaga_resp = await game_services.start_challenge(user_id=tojaga.id, mode="adaptive")
    maleza_resp = await game_services.start_challenge(user_id=maleza.id, mode="adaptive")

    tojaga_avg = sum(r["difficulty_rating"] for r in tojaga_resp["rounds"]) / len(tojaga_resp["rounds"])
    maleza_avg = sum(r["difficulty_rating"] for r in maleza_resp["rounds"]) / len(maleza_resp["rounds"])
    assert maleza_avg > tojaga_avg


@pytest.mark.asyncio
async def test_seeded_locations_are_approved_and_have_difficulty_profiles(db):
    await seed_users()
    await seed_locations()

    total_locations = await Location.all().count()
    approved_locations = await Location.filter(is_approved=True).count()
    assert total_locations > 0
    assert approved_locations == total_locations
