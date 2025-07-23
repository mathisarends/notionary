"""
# Notionary: Basic Markdown Demo
===============================

A demo showing basic markdown formatting in Notion pages.
Perfect for testing standard markdown elements!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demo of basic markdown formatting."""

    print("🚀 Notionary Basic Markdown Demo")
    print("=" * 34)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        basic_content = """
        ### Text Formatting
        This paragraph demonstrates **bold text**, *italic text*, and `inline code`. 
        You can also combine them like ***bold and italic*** or **bold with `code`**.

        ### Bulleted Lists
        Here are some key features of Notionary:
        - Simple API for Notion automation
        - Async/await support for modern Python
        - Fuzzy search capabilities
        - Extended markdown syntax
        - Type safety with full hints
        - Automatic retry mechanisms

        ### Numbered Lists
        Getting started with Notionary:
        1. Install the package via pip
        2. Set up your Notion integration
        3. Connect to your workspace
        4. Create your first page
        5. Add content with markdown
        6. Enjoy the automation!

        ---

        ### Inline Code and Links
        Use `NotionPage.from_page_name()` to find pages by name.
        The `append_markdown()` method adds content to existing pages.
        Variables like `DATABASE_NAME` should be set in your configuration.
        
        ---

        ### Important Notes
        - Always use `await` with async functions
        - Keep your *API tokens* secure
        - Test with **small batches** first
        - Use `try/except` blocks for error handling

        ### Code Variables
        Common variables you'll use:
        - `page_id` for specific page references
        - `database_name` for fuzzy database matching
        - `content` for markdown text
        - `properties` for page metadata
        """

        # Add the markdown content to the page
        print("\n📝 Adding basic markdown examples...")
        await page.append_markdown(basic_content)

        print(f"\n✅ Successfully added basic markdown to '{page.title}'!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
