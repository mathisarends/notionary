"""
# Notionary: Table Element Markdown Demo
=======================================

A demo showing how to add custom table elements to Notion pages using Markdown.
Perfect for demonstrating TableElement syntax!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demo of adding TableElement markdown to a Notion page."""

    print("🚀 Notionary Table Element Demo")
    print("=" * 34)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        table_content = """
        ## 📊 Table Element Examples

        ### Product Catalog
        | Product | Price | Stock | Status |
        | ------- | ----- | ----- | ------ |
        | Widget A | $10.99 | 42 | Available |
        | Widget B | $14.99 | 27 | Available |
        | Widget C | $8.50 | 0 | Out of Stock |

        ### Team Directory
        | Name | Role | Department | Email |
        | ---- | ---- | ---------- | ----- |
        | John Smith | Manager | Marketing | john@company.com |
        | Jane Doe | Director | Sales | jane@company.com |
        | Bob Johnson | Developer | Engineering | bob@company.com |

        ### Project Status
        | Project | Priority | Progress | Due Date |
        | ------- | -------- | -------- | -------- |
        | Website Redesign | High | 75% | 2025-08-15 |
        | Mobile App | Medium | 45% | 2025-09-30 |
        | API Integration | Low | 20% | 2025-10-15 |
        """

        # Add the markdown content to the page
        print("\n📝 Adding Table Element examples...")
        await page.append_markdown(table_content)

        print(f"\n✅ Successfully added table examples to '{page.title}'!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
