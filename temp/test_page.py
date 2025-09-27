from notionary import NotionPage

PAGE = "Clean Code Udemy Course"


async def main():
    page = await NotionPage.from_title(PAGE)

    print("page.url", page.url)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
