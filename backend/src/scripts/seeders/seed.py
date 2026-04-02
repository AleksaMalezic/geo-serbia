import asyncio

from tortoise import Tortoise
from src.core.settings import TORTOISE_ORM

from src.scripts.seeders.location_seeder import seed as location_seeder
from src.scripts.seeders.user_seeder import seed as user_seeder


async def main():
    should_close = False
    if not Tortoise._inited:
        await Tortoise.init(config=TORTOISE_ORM)
        should_close = True
    try:
        await user_seeder()
        await location_seeder()
        print("All seeders completed.")
    finally:
        if should_close:
            await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
