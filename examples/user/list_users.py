"""List workspace members and search by name."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        users = await notion.users.list(filter="person")
        for user in users:
            print(f"{user.name} – {user.email}")

        results = await notion.users.search("mathis")
        for user in results:
            print(f"Found: {user.name}")


if __name__ == "__main__":
    asyncio.run(main())
