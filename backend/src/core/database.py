from tortoise import Tortoise
from src.core.settings import settings


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.DATABASE_ADDRESS,
                "port": settings.DATABASE_PORT,
                "user": settings.DATABASE_USER,
                "password": settings.DATABASE_PASS,
                "database": settings.DATABASE_NAME,
                "minsize": 5,
                "maxsize": 20,
            },
        }
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


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    print("Database connected and schemas generated.")


async def close_db():
    await Tortoise.close_connections()
    print("Database connection closed.")
