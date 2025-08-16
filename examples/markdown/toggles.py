import asyncio
from notionary import NotionPage


async def main():
    """Minimal column test to isolate parsing issues."""

    try:
        page = await NotionPage.from_page_name("Jarvis Clipboard")

        markdown = """
        +++ My Toggle
        This is content inside the toggle.
        More content here.
        +++

        +++ Another Toggle
        Different content.
        +++
        +++# Chapter 1
        Content for chapter 1.
        Some paragraphs here.
        +++

        +++## Section A
        Content for section A.
        +++

        +++### Subsection
        Detailed content.
        +++
        """

        print("markdown_content", markdown)

        print("=" * 50)

        await page.append_markdown(markdown)
        print("✅ Success!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())


