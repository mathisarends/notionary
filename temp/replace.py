from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Notionary Demo")

    print(f"Page found: {page.title}")
    await page.replace_content("This is shit")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
