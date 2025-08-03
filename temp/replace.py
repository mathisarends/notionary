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
    | ::: column
    | | ## Left Column  
    | | This is content in the left column.
    | | - First point
    | | - Second point
    | |
    | | ### Employee Data
    | | | Name   | Age | City     | Department |
    | | | ------ | --- | -------- | ---------- |
    | | | Alice  | 30  | Berlin   | Engineering|
    | | | Bob    | 25  | Hamburg  | Marketing  |
    | | | Carol  | 28  | Munich   | Design     |
    | | | David  | 32  | Cologne  | Sales      |
    | |
    | | Some text after the table.
    | ::: column
    | | ## Right Column
    | | This is content in the right column.
    | | - Another point
    | | - Final point
    | |
    | | ```python
    | | def hello_world():
    | |     print("Hello from the right column!")
    | |     return "Success"
    | | ```
    | |
    | | > This is a quote block in the right column.
    | | > It can span multiple lines.

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
