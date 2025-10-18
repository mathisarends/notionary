import asyncio

from notionary import NotionDataSource

# Replace with your desired page title
DATA_SOURCE_URL = "https://www.notion.so/your-datasource-url"


async def main() -> None:
    data_source = await NotionDataSource.from_url(DATA_SOURCE_URL)
    print(f"Found datasource: {data_source.title} (URL: {data_source.url})")

    schema_description = await data_source.get_schema_description()
    print(schema_description)


if __name__ == "__main__":
    asyncio.run(main())
