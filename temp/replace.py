from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")

    print(f"Page found: {page.title}")

    todos = """
- [ ] First todo
- [x] Completed todo
- [ ] Another todo
"""
    await page.append_markdown(todos)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
