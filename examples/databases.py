import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        database = await notion.databases.list()
        for db in database:
            print(f"{db.title} ({db.url})")


if __name__ == "__main__":
    asyncio.run(main())
