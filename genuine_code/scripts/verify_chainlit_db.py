import asyncio, os, asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def verify():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    tables = ["User", "Thread", "Step", "Element", "Feedback"]
    print("Verifying tables...")
    all_good = True
    for t in tables:
        try:
            res = await conn.fetchval(f'SELECT count(*) FROM "{t}"')
            print(f"Table '{t}' exists. Rows: {res}")
        except Exception as e:
            print(f"Table '{t}' check failed: {e}")
            all_good = False
    
    await conn.close()
    if all_good:
        print("Verification SUCCESS: All tables exist.")
    else:
        print("Verification FAILED: Some tables missing.")

if __name__ == "__main__":
    asyncio.run(verify())
