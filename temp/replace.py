from notionary import NotionPage


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")
    print(f"Page found: {page.title}")

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

    ::: columns
    ::: column
    ## Left Column
    This is content in the left column.
    - First point
    - Second point

    ```python
    def hello():
        print('Hello from inside a column!')
    ```

    | Name   | Age | City     |
    | ------ | --- | -------- |
    | Alice  | 30  | Berlin   |
    | Bob    | 25  | Hamburg  |
    | Carol  | 28  | Munich   |

    :::
    ::: column
    ## Right Column
    This is content in the right column.
    - Another point
    - Final point
    :::
    :::

    Regular paragraph after everything.
    """

    edge_result = await page.append_markdown(test_markdown, append_divider=True)
    if edge_result:
        print("✅ Edge case test with columns completed successfully")
    else:
        print("❌ Edge case test with columns failed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
