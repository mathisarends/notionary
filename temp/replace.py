from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")
    print(f"Page found: {page.title}")

    # Test markdown with advanced capability-based features
    test_markdown = """## 🚀 Capability-based Parser Test

    +++ Toggle Title
    | Nested content line 1
    | +++ Nested Toggle
    | | Double nested content line 1
    | | Double nested content line 2
    | Nested content line 2
    
    +## Wichtige Infos
    | Das ist ein Detail
    | Noch mehr Details

    ```python
    def hello():
        print('Hello, Notion!')
    ```
    """

    edge_result = await page.append_markdown(test_markdown, append_divider=True)
    if edge_result:
        print("✅ Edge case test completed successfully")
    else:
        print("❌ Edge case test failed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
