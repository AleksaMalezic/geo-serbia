import pytest


async def authenticate(client, username: str, password: str):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    assert resp.json().get("success") is True


@pytest.mark.asyncio
async def test_locations_default_only_approved(client, user):
    await authenticate(client, "testuser", "Password123!")

    # Create a location (will be unapproved by default)
    resp = await client.post(
        "/api/v1/locations/",
        data={
            "name": "Hidden Location",
            "description": "Unapproved",
            "latitude": 45.0,
            "longitude": 20.0,
        },
    )
    assert resp.status_code == 200

    # Should not appear in default list
    list_resp = await client.get("/api/v1/locations/", params={"page": 1, "limit": 1})
    assert list_resp.status_code == 200
    items = list_resp.json().get("data", {}).get("items", [])
    assert items == []


@pytest.mark.asyncio
async def test_admin_can_approve_location(client, user, admin_user):
    await authenticate(client, "testuser", "Password123!")

    create_resp = await client.post(
        "/api/v1/locations/",
        data={
            "name": "Approve Me",
            "description": "Pending",
            "latitude": 45.0,
            "longitude": 20.0,
        },
    )
    assert create_resp.status_code == 200
    location_id = create_resp.json().get("data", {}).get("id")

    await authenticate(client, "admin", "AdminPass123!")
    approve_resp = await client.post(
        f"/api/v1/locations/{location_id}/approve",
    )
    assert approve_resp.status_code == 200

    list_resp = await client.get("/api/v1/locations/", params={"page": 1, "limit": 1})
    items = list_resp.json().get("data", {}).get("items", [])
    assert len(items) == 1
    assert items[0]["name"] == "Approve Me"
