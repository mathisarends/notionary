from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")

    print(f"Page found: {page.title}")

    todos = """
- [ ] First todo
- [x] Completed todo
- [ ] Another todo
"""
    cleared_content  = await page.clear_page_content()
    print(f"Cleared content: {cleared_content}")
    
    appended_content = await page.append_markdown(todos, append_divider=True)
    print(f"Appended content: {appended_content}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())