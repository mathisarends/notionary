"""
# Notionary: Code Block Element Demo
===================================

Simple demo showing how to create syntax-highlighted code blocks using MarkdownBuilder.
Perfect for documentation, tutorials, and technical content!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_code_examples() -> str:
    """Creates code block examples using MarkdownBuilder."""
    return (
        MarkdownBuilder()
        .h2("💻 Code Block Elements")
        .paragraph("Code blocks provide syntax highlighting for various programming languages.")
        .space()
        .code_block(
            code='''def hello_notionary():
    """Greet the Notionary library."""
    print("Hello, Notionary!")
    return {"status": "success", "message": "Ready to automate!"}

# Call the function
result = hello_notionary()
print(f"Result: {result}")''',
            language="python",
            caption="Basic Python function with return value",
        )
        .space()
        .callout(
            text="Notion supports 40+ programming languages for syntax highlighting, including Python, JavaScript, SQL, YAML, and more!",
            emoji="🎨",
        )
        .build()
    )


async def main():
    """Demo of adding code block elements to a Notion page."""

    print("🚀 Notionary Code Block Demo")
    print("=" * 30)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_title(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"└── URL: {page.url}")

        print("\n💻 Creating code examples...")
        content = create_code_examples()

        print("✨ Adding content to page...")
        await page.append_markdown(content)

        print("\n✅ Successfully added code block examples!")
        print(f"🌐 View at: {page.url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
