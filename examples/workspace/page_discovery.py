import asyncio

from notionary import NotionWorkspace


async def main() -> None:
    workspace = await NotionWorkspace.from_current_integration()

    async for page in workspace.get_pages_stream():
        print(f"Data Source: {page.title} (URL: {page.url})")


if __name__ == "__main__":
    asyncio.run(main())
