import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"
        )
    )

    PRODUCTION: bool = False
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_SECRET: str = "supersecretkey"
    REFRESH_TOKEN_SECRET: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ACCESS_COOKIE_NAME: str = "access_token"
    REFRESH_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 2

    DATABASE_USER: str
    DATABASE_PASS: str
    DATABASE_ADDRESS: str
    DATABASE_PORT: str
    DATABASE_NAME: str


settings: Settings = Settings()

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
                "minsize": 10,
                "maxsize": 20,
                "max_queries": 50000,  # Max queries per connection before recycling
                "max_inactive_connection_lifetime": 300,
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
