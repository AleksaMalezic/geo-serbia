import pytest


async def authenticate(client, username: str, password: str):
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_resp.status_code == 200
    assert login_resp.json().get("success") is True


@pytest.mark.asyncio
async def test_register_and_login(client):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "email": "newuser@example.com", "password": "Password123!"},
    )
    assert register_resp.status_code == 200
    data = register_resp.json().get("data", {})
    assert data.get("username") == "newuser"

    await authenticate(client, "newuser", "Password123!")


@pytest.mark.asyncio
async def test_me_stats(client, user):
    await authenticate(client, "testuser", "Password123!")

    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    payload = me_resp.json().get("data", {})
    assert payload.get("username") == "testuser"
    assert "stats" in payload
