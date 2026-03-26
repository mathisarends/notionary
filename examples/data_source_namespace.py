import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        data_sources = await notion.data_sources.list()
        for data_source in data_sources:
            print(f"  {data_source.title} – {data_source.id}")


if __name__ == "__main__":
    asyncio.run(main())
