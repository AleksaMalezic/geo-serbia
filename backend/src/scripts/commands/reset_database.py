import asyncio
import os
import sys
from tortoise import BaseDBAsyncClient, Tortoise, connections
from src.core.settings import TORTOISE_ORM


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


async def _drop_postgres(conn):
    await conn.execute_script(
        "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
    )


async def reset(confirm=True, reseed=True):
    if confirm:
        answer: str = (
            input("This will DROP all tables. Type 'yes' to continue: ").strip().lower()
        )

        if answer != "yes":
            print("Canceled.")
            return

    await Tortoise.init(config=TORTOISE_ORM)

    try:
        conn: BaseDBAsyncClient = connections.get("default")
        db_config: str = TORTOISE_ORM.get("connections", {}).get("default", {})
        db_url: str = (
            db_config if isinstance(db_config, str) else db_config.get("engine", "")
        )

        if "postgres" in db_url.lower() or "asyncpg" in db_url.lower():
            await _drop_postgres(conn)
        else:
            conn_type: str = str(type(conn)).lower()
            if "postgres" in conn_type or "asyncpg" in conn_type:
                await _drop_postgres(conn)
            else:
                print(f"Unsupported database type. Connection: {conn_type}")
                print(f"Database URL: {db_url}")
                return

        await Tortoise.generate_schemas(safe=True)
        print("Schema regenerated.")

        if reseed:
            from src.scripts.seeders.seed import main as seed_all_main

            await seed_all_main()
    finally:
        await Tortoise.close_connections()


async def main():
    confirm: bool = "--yes" not in sys.argv
    reseed: bool = "--no-seed" not in sys.argv
    await reset(confirm=confirm, reseed=reseed)


if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(main())
