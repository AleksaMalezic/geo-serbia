import sys
from pathlib import Path
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.boot.main import app as fastapi_app
from src.domains.users.models import User
from src.domains.users.services import hash_password
from src.domains.locations.models import Location


TEST_DB_URL = "sqlite://:memory:"

TORTOISE_TEST_CONFIG = {
    "connections": {
        "default": TEST_DB_URL,
    },
    "apps": {
        "models": {
            "models": [
                "src.domains.locations.models",
                "src.domains.users.models",
                "src.domains.games.models",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "UTC",
}


@pytest.fixture(scope="function")
async def db():
    await Tortoise.init(config=TORTOISE_TEST_CONFIG)
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()


@pytest.fixture
async def app(db) -> FastAPI:
    fastapi_app.router.on_startup.clear()
    fastapi_app.router.on_shutdown.clear()
    return fastapi_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def user(db) -> User:
    return await User.create(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Password123!"),
        is_admin=False,
    )


@pytest.fixture
async def admin_user(db) -> User:
    return await User.create(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("AdminPass123!"),
        is_admin=True,
    )


@pytest.fixture
async def approved_location(db, user: User) -> Location:
    return await Location.create(
        name="Test Location",
        description="Test description",
        latitude=45.0,
        longitude=20.0,
        created_by=user,
        is_approved=True,
    )
