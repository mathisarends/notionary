from notionary.database.database import NotionDatabase


async def main() -> None:
    print("ich bin hier du bist da")
    database = await NotionDatabase.from_title("Wissen / Notizen")
    print("database", database.title)

    data_sources = await database.get_data_sources()
    for ds in data_sources:
        print(" - data source:", ds)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
