import asyncio, os, asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables.")
    exit(1)

async def init_db():
    print(f"Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    print("Creating tables...")

    queries = [
        """
        CREATE TABLE IF NOT EXISTS "User" (
            "id" TEXT PRIMARY KEY,
            "identifier" TEXT NOT NULL UNIQUE,
            "metadata" JSONB NOT NULL DEFAULT '{}',
            "createdAt" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS "Thread" (
            "id" TEXT PRIMARY KEY,
            "createdAt" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            "deletedAt" TIMESTAMPTZ,
            "name" TEXT,
            "userId" TEXT REFERENCES "User"("id") ON DELETE SET NULL,
            "tags" TEXT[],
            "metadata" JSONB DEFAULT '{}'
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS "Step" (
            "id" TEXT PRIMARY KEY,
            "name" TEXT,
            "type" TEXT NOT NULL,
            "threadId" TEXT NOT NULL REFERENCES "Thread"("id") ON DELETE CASCADE,
            "parentId" TEXT REFERENCES "Step"("id") ON DELETE CASCADE,
            "showInput" TEXT,
            "input" TEXT,
            "output" TEXT,
            "metadata" JSONB DEFAULT '{}',
            "isError" BOOLEAN DEFAULT FALSE,
            "startTime" TIMESTAMPTZ,
            "endTime" TIMESTAMPTZ,
            "createdAt" TIMESTAMPTZ DEFAULT NOW(),
            "generationId" TEXT
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS "Element" (
            "id" TEXT PRIMARY KEY,
            "threadId" TEXT REFERENCES "Thread"("id") ON DELETE CASCADE,
            "stepId" TEXT REFERENCES "Step"("id") ON DELETE CASCADE,
            "type" TEXT,
            "url" TEXT,
            "chainlitKey" TEXT,
            "name" TEXT NOT NULL,
            "display" TEXT,
            "objectKey" TEXT,
            "size" TEXT,
            "language" TEXT,
            "page" INTEGER,
            "mime" TEXT,
            "props" JSONB DEFAULT '{}',
            "metadata" JSONB DEFAULT '{}'
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS "Feedback" (
            "id" TEXT PRIMARY KEY,
            "stepId" TEXT NOT NULL REFERENCES "Step"("id") ON DELETE CASCADE,
            "value" FLOAT NOT NULL,
            "comment" TEXT,
            "name" TEXT
        );
        """
    ]

    for query in queries:
        try:
            await conn.execute(query)
            # print(f"Executed query successfully.")
        except Exception as e:
            print(f"Error executing query: {e}")
            # print(f"Query: {query}")

    print("Tables created successfully.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())
