"""
# Notionary: Basic Markdown Demo
===============================

A demo showing basic markdown formatting in Notion pages using MarkdownBuilder.
Perfect for testing the fluent interface and standard markdown elements!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_basic_markdown_content() -> str:
    """Creates basic markdown content using the fluent MarkdownBuilder interface."""

    return (
        MarkdownBuilder()
        # Text Formatting Section
        .h3("Text Formatting")
        .paragraph(
            "This paragraph demonstrates **bold text**, *italic text*, and `inline code`. "
            "You can also combine them like ***bold and italic*** or **bold with `code`**."
        )
        .space()
        # Bulleted Lists Section
        .h3("Bulleted Lists")
        .paragraph("Here are some key features of Notionary:")
        .bulleted_list(
            [
                "Simple API for Notion automation",
                "Async/await support for modern Python",
                "Fuzzy search capabilities",
                "Extended markdown syntax",
                "Type safety with full hints",
                "Automatic retry mechanisms",
            ]
        )
        .space()
        # Numbered Lists Section
        .h3("Numbered Lists")
        .paragraph("Getting started with Notionary:")
        .numbered_list(
            [
                "Install the package via pip",
                "Set up your Notion integration",
                "Connect to your workspace",
                "Create your first page",
                "Add content with markdown",
                "Enjoy the automation!",
            ]
        )
        .divider()
        # Inline Code and Links Section
        .h3("Inline Code and Links")
        .paragraph("Use `NotionPage.from_page_name()` to find pages by name.")
        .paragraph("The `append_markdown()` method adds content to existing pages.")
        .paragraph("Variables like `DATABASE_NAME` should be set in your configuration.")
        .divider()
        # Important Notes Section
        .h3("Important Notes")
        .bulleted_list(
            [
                "Always use `await` with async functions",
                "Keep your *API tokens* secure",
                "Test with **small batches** first",
                "Use `try/except` blocks for error handling",
            ]
        )
        .space()
        # Code Variables Section
        .h3("Code Variables")
        .paragraph("Common variables you'll use:")
        .bulleted_list(
            [
                "`page_id` for specific page references",
                "`database_name` for fuzzy database matching",
                "`content` for markdown text",
                "`properties` for page metadata",
            ]
        )
        # Callout for extra emphasis
        .space()
        .callout(
            text="Remember to always handle exceptions gracefully when working with external APIs!",
            emoji="⚠️",
        )
        .build()
    )


async def main():
    """Demo of basic markdown formatting using MarkdownBuilder."""

    print("🚀 Notionary Basic Markdown Builder Demo")
    print("=" * 42)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_title(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        print("\n🔨 Building content with MarkdownBuilder...")
        basic_content = create_basic_markdown_content()

        print("📋 Content Preview:")
        print("-" * 50)
        preview = basic_content[:150] + "..." if len(basic_content) > 150 else basic_content
        print(preview)
        print("-" * 50)

        print("\n📝 Adding markdown content to page...")
        await page.append_markdown(basic_content)

        print("\n✅ Successfully added content using MarkdownBuilder!")
        print("🌐 Visit your page: {page.url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Troubleshooting:")
        print("   • Check if the page name exists in your workspace")
        print("   • Verify your Notion API credentials")
        print("   • Ensure the page has edit permissions")


if __name__ == "__main__":
    asyncio.run(main())
