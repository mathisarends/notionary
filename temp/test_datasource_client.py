from notionary.database.database import NotionDatabase


async def main() -> None:
    data_source = await NotionDatabase.from_title("Wissen / Notizen")

    print("data_source.id", data_source.id)
    print("data_source.title", data_source.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
