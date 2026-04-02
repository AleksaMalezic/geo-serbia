import pytest


async def authenticate(client, username: str, password: str):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    assert resp.json().get("success") is True


@pytest.mark.asyncio
async def test_play_round_limit(client, user, approved_location):
    await authenticate(client, "testuser", "Password123!")

    for _ in range(5):
        resp = await client.post(
            "/api/v1/game/play",
            params={
                "location_id": approved_location.id,
                "guessed_latitude": 45.1,
                "guessed_longitude": 20.1,
            },
        )
        assert resp.status_code == 200

    sixth = await client.post(
        "/api/v1/game/play",
        params={
            "location_id": approved_location.id,
            "guessed_latitude": 45.1,
            "guessed_longitude": 20.1,
        },
    )
    assert sixth.status_code == 400
