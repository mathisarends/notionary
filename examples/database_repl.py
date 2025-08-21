"""
# Notionary: Database Demo
=========================

A quick demo showing basic database information retrieval and operations using MarkdownBuilder.
Perfect for getting started with Notionary databases!

SETUP: Replace DATABASE_NAME with an existing database in your Notion workspace.
"""

import asyncio
import traceback
from venv import create

from notionary import MarkdownBuilder, NotionDatabase, NotionPage
import notionary

# REPLACE DATABASE NAME
DATABASE_NAME = "Wissen/Notizen"


def create_demo_page_content() -> str:
    """Creates demo page content using the fluent MarkdownBuilder interface."""
    builder = MarkdownBuilder()

    return builder.code(
        code="""from notionary import NotionDatabase

        # Find database by name (fuzzy matching)
        db = await NotionDatabase.from_database_name("Projects")

        # Create a new page
        page = await db.create_blank_page()
        await page.set_title("New Project")""",
        language="python",
        caption="Connect to a Notion database and create a page",
    ).build()


async def main():
    """Simple demo of NotionDatabase basic operations."""

    print("🚀 Notionary Database Builder Demo")
    print("=" * 38)

    try:
        page = await NotionPage.from_page_name("Jarvis Clipboard")
        await page.append_markdown(create_demo_page_content())

        print("did it")

    except Exception as e:
        print("❌ Error: {}".format(e))
        print("🔍 Full traceback:\n{}".format(traceback.format_exc()))
        print("💡 Troubleshooting:")
        print("   • Check if the database name exists in your workspace")
        print("   • Verify your Notion API credentials")
        print("   • Ensure database has create permissions")


if __name__ == "__main__":
    asyncio.run(main())
