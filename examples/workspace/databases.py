"""List and manage databases in the workspace."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        databases = await notion.databases.list()
        for db in databases:
            print(f"{db.title} ({db.url})")

        db = await notion.databases.find("Tasks")
        await db.set_description("Tracks all current tasks and their status.")
        await db.set_icon("✅")
        print(f"Updated: {db.title}")


if __name__ == "__main__":
    asyncio.run(main())
