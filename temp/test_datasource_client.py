from notionary import NotionDataSource


async def main():
    data_source = await NotionDataSource.from_title("Wissen / Notizen")

    print("data_source.id", data_source.id)
    print("data_source.title", data_source.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
