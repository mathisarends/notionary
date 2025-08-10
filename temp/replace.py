from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")
    print(f"Page found: {page.title}")

    test_markdown = """## 🚀 Capability-based Parser Test

    ```python
    print("hello world")
    ```

    
    +### Spinnen
    | sind wilde
    | tiere    


    | Name   | Value |
    |--------|-------|
    | Alpha  | 1     |
    | Beta   | 2     |
    | Gamma  | 3     |

    """

    edge_result = await page.append_markdown(test_markdown, append_divider=True)
    if edge_result:
        print("✅ Edge case test with columns completed successfully")
    else:
        print("❌ Edge case test with columns failed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
