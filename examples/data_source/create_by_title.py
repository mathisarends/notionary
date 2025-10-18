import asyncio

from notionary import NotionDataSource

# Replace with your desired page title
DATA_SOURCE_TITLE = "Inbox"


async def main() -> None:
    data_source = await NotionDataSource.from_title(DATA_SOURCE_TITLE)
    print(f"Found datasource: {data_source.title} (URL: {data_source.url})")

    schema_description = await data_source.get_schema_description()
    print(schema_description)


if __name__ == "__main__":
    asyncio.run(main())
