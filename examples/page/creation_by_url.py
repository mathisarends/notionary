import asyncio

from notionary import NotionPage

# Replace with your desired page url (just copy from notion)
PAGE_URL = "https://www.notion.so/your-page-url"


async def main() -> None:
    page = await NotionPage.from_url(PAGE_URL)
    print(f"Found page: {page.title} (URL: {page.url})")

    content = await page.get_markdown_content()
    print("Page content in Markdown:")
    print(content)


if __name__ == "__main__":
    asyncio.run(main())
