import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        data_source = await notion.data_sources.from_title("Projekte")
        await data_source.set_title("Neuer Titel")
        await data_source.set_icon_emoji("🚀")
        print("properties", data_source.properties)


if __name__ == "__main__":
    asyncio.run(main())
