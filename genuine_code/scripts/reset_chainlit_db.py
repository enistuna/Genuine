import asyncio, os, asyncpg
from dotenv import load_dotenv
from init_chainlit_db import init_db

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def reset_db():
    print(f"Connecting to database to reset tables...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    tables = ["Feedback", "Element", "Step", "Thread", "User"]
    print("Dropping tables...")

    for t in tables:
        try:
            await conn.execute(f'DROP TABLE IF EXISTS "{t}" CASCADE')
            print(f"Dropped table {t}")
        except Exception as e:
            print(f"Error dropping table {t}: {e}")

    await conn.close()
    print("Tables dropped. Initializing new schema...")
    await init_db()

if __name__ == "__main__":
    asyncio.run(reset_db())
