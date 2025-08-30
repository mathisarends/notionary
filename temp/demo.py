"""
demo_fun_single_column_rickroll.py
Playful page: 2-column hero (Rickroll + meme), then text, then a valid Mermaid diagram.
UPDATED: Now using comprehensive content from database.py example
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Notionary Demo"


def create_demo_page_content():
    """Creates demo page content using the fluent MarkdownBuilder interface from database.py example."""
    
    from notionary import MarkdownBuilder
    
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
        .paragraph("Built with ❤️ for the Notion community.")
        .build()
    )


async def main():
    print(f"🔎 Loading page by name: {PAGE_NAME!r}")
    page = await NotionPage.from_page_name(PAGE_NAME)

    print("🧱 Appending blocks via Builder API …")
    
    # Use the comprehensive content from database.py example
    content = create_demo_page_content()
    
    await page.append_markdown(content)

    print("✅ Done! Enjoy your very serious, extremely professional docs.")


if __name__ == "__main__":
    asyncio.run(main())