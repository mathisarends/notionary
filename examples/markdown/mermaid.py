import asyncio

from notionary import NotionPage
from notionary.markdown.markdown_builder import MarkdownBuilder


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")
    builder = MarkdownBuilder()

    builder.h1("Mermaid Diagram Test")
    builder.mermaid(
        """graph TD
        A[Start] --> B{Is it working?}
        B -->|Yes| C[Great]
        B -->|No| D[Fix it]
        C --> E[Done]
        D --> E[Done]""",
        "Simple mermaid flow",
    )

    markdown = builder.build()
    print("Generated markdown:\n", markdown)
    await page.append_markdown(markdown)
    print("✅ Mermaid appended to Jarvis Clipboard")


if __name__ == "__main__":
    asyncio.run(main())
