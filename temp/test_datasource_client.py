from notionary.data_source.data_source_http_client import NotionDataSourceHttpClient


async def main():
    client = NotionDataSourceHttpClient("1a6389d5-7bd3-804d-ac1d-000b852bf920")

    data_source = await client.get_data_source()

    print("data_source.title", data_source.title)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
