"""Get the current bot identity and workspace info."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        bot = await notion.users.me()
        print(f"Bot: {bot.name} ({bot.workspace_name})")


if __name__ == "__main__":
    asyncio.run(main())
