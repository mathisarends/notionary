"""
# Notionary: Database Demo
=========================

A quick demo showing basic database information retrieval and operations using MarkdownBuilder.
Perfect for getting started with Notionary databases!

SETUP: Replace DATABASE_NAME with an existing database in your Notion workspace.
"""

import asyncio
import traceback

from notionary import MarkdownBuilder, NotionDatabase

# REPLACE DATABASE NAME
DATABASE_NAME = "Wissen/Notizen"


def create_demo_page_content() -> str:
    """Creates demo page content using the fluent MarkdownBuilder interface."""

    return (
        MarkdownBuilder()
        .callout(
            text="Welcome to Notionary! The easiest way to automate Notion with Python",
            emoji="🎯",
        )
        .space()
        # Main features section
        .h2("Why Choose Notionary?")
        .numbered_list(
            [
                "**Simple API** - Connect to databases and pages with just `one line of code`",
                "**Extended Markdown** - Use Notion-specific elements like *callouts*, *toggles*, and *embeds*",
                "**Async Support** - Built for modern Python with full `async/await` support",
                "**Smart Features** - *Fuzzy search*, *batch processing*, and *automatic retries*",
                "**Type Safety** - Full type hints for better IDE support",
            ]
        )
        .divider()
        .h2("⚡ Quick Start Examples")
        .h3("Database Connection")
        .code(
            code="""from notionary import NotionDatabase

            # Find database by name (fuzzy matching)
            db = await NotionDatabase.from_database_name("Projects")

            # Create a new page
            page = await db.create_blank_page()
            await page.set_title("New Project")""",
            language="python",
            caption="Connect to a Notion database and create a page",
        )
        .space()
        .h3("Page Operations")
        .code(
            code="""from notionary import NotionPage

            # Find page by name
            page = await NotionPage.from_page_name("Meeting Notes")

            # Update content
            await page.append_markdown("## Action Items\\n- [ ] Follow up with team")

            # Set properties
            await page.set_property_value_by_name("Status", "In Progress")""",
            language="python",
            caption="Update content and properties on an existing page",
        )
        .space()
        .h3("MarkdownBuilder Usage")
        .code(
            code="""from notionary import MarkdownBuilder

            # Build content with fluent interface
            content = (
                MarkdownBuilder()
                .h2("Project Updates")
                .callout("Important milestone reached!", emoji="🎉")
                .table(
                    headers=["Task", "Status", "Owner"],
                    rows=[
                        ["Design Review", "Complete", "Alice"],
                        ["Development", "In Progress", "Bob"],
                        ["Testing", "Pending", "Charlie"]
                    ]
                )
                .build()
            )

            await page.append_markdown(content)""",
            language="python",
            caption="Using MarkdownBuilder for structured content creation",
        )
        .divider()
        .h2("🌟 Advanced Features")
        .table(
            headers=["Feature", "Description", "Example"],
            rows=[
                [
                    "Fuzzy Search",
                    "Find databases/pages by partial names",
                    "`from_database_name('Proj')`",
                ],
                [
                    "Batch Operations",
                    "Process multiple items efficiently",
                    "`await db.get_all_pages()`",
                ],
                [
                    "Auto Retries",
                    "Handles API rate limits automatically",
                    "Built-in exponential backoff",
                ],
                ["Type Safety", "Full typing support", "IDE autocompletion & hints"],
                [
                    "Async Support",
                    "Non-blocking operations",
                    "`async/await` throughout",
                ],
            ],
        )
        .space()
        .callout(
            text="Pro tip: Use MarkdownBuilder for complex content and raw strings for simple text!",
            emoji="💡",
        )
        .space()
        .paragraph("Built with ❤️ for the Notion community.")
        .build()
    )


async def main():
    """Simple demo of NotionDatabase basic operations."""

    print("🚀 Notionary Database Builder Demo")
    print("=" * 38)

    try:
        print(f"🔍 Loading database: '{DATABASE_NAME}'")
        db = await NotionDatabase.from_database_name(DATABASE_NAME)

        # Display basic database information
        print(f"\n{db.emoji} Database Information:")
        print(f"├── Title: {db.title}")
        print(f"├── ID: {db.id}")
        print(f"└── Visit at: {db.url}")

        print("\n🔨 Building demo page content...")
        content = create_demo_page_content()

        print("📋 Content Preview:")
        print("-" * 50)
        preview = content[:150] + "..." if len(content) > 150 else content
        print(preview)
        print("-" * 50)

        print("\n📄 Creating a new page...")
        page = await db.create_blank_page()

        print("🎨 Setting page properties...")
        await page.set_title("Notionary Demo")
        await page.set_emoji_icon("🚀")
        await page.set_random_gradient_cover()

        print("📝 Adding structured content using MarkdownBuilder...")
        await page.append_markdown(content)

        print("\n✅ Demo page created successfully!")
        print(f"├── Database: {db.title} (ID: {db.from_database_id})")
        print(f"├── Page title: {page.title}")
        print(f"├── Page emoji: {page.emoji_icon}")
        print(f"└── Visit at: {page.url}")

        print("\n🎉 MarkdownBuilder demo completed!")

    except Exception as e:
        print("❌ Error: {}".format(e))
        print("🔍 Full traceback:\n{}".format(traceback.format_exc()))
        print("💡 Troubleshooting:")
        print("   • Check if the database name exists in your workspace")
        print("   • Verify your Notion API credentials")
        print("   • Ensure database has create permissions")


if __name__ == "__main__":
    asyncio.run(main())
