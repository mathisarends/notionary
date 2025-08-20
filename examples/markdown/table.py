"""
# Notionary: Table Element Markdown Demo
=======================================

A demo showing how to add custom table elements to Notion pages using MarkdownBuilder.
Perfect for demonstrating TableElement syntax with the fluent interface!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_table_examples_content() -> str:
    """Creates table examples using the fluent MarkdownBuilder interface."""

    return (
        MarkdownBuilder()
        .h2("📊 Table Element Examples")
        .paragraph(
            "Tables are perfect for organizing structured data in a clear, readable format."
        )
        .space()
        .h3("Product Catalog")
        .table(
            headers=["Product", "Price", "Stock", "Status"],
            rows=[
                ["Widget A", "$10.99", "42", "Available"],
                ["Widget B", "$14.99", "27", "Available"],
                ["Widget C", "$8.50", "0", "Out of Stock"],
                ["Widget D", "$22.99", "15", "Available"],
                ["Widget E", "$7.25", "8", "Low Stock"],
            ],
        )
        .space()
        .h3("Team Directory")
        .table(
            headers=["Name", "Role", "Department", "Email"],
            rows=[
                ["John Smith", "Manager", "Marketing", "john@company.com"],
                ["Jane Doe", "Director", "Sales", "jane@company.com"],
                ["Bob Johnson", "Developer", "Engineering", "bob@company.com"],
                ["Alice Chen", "Designer", "UX/UI", "alice@company.com"],
                ["Mike Wilson", "Analyst", "Data Science", "mike@company.com"],
            ],
        )
        .space()
        .h3("Project Status")
        .table(
            headers=["Project", "Priority", "Progress", "Due Date"],
            rows=[
                ["Website Redesign", "High", "75%", "2025-08-15"],
                ["Mobile App", "Medium", "45%", "2025-09-30"],
                ["API Integration", "Low", "20%", "2025-10-15"],
                ["Database Migration", "High", "90%", "2025-08-01"],
                ["Security Audit", "Critical", "30%", "2025-08-30"],
            ],
        )
        .space()
        .h3("Performance Metrics")
        .table(
            headers=["Metric", "Current", "Target", "Trend"],
            rows=[
                ["Response Time", "245ms", "200ms", "⬇️ Improving"],
                ["Uptime", "99.8%", "99.9%", "➡️ Stable"],
                ["Error Rate", "0.02%", "0.01%", "⬇️ Improving"],
                ["Throughput", "1.2K/sec", "1.5K/sec", "⬆️ Growing"],
                ["Memory Usage", "78%", "70%", "⬇️ Optimizing"],
            ],
        )
        .divider()
        .h3("📋 Table Best Practices")
        .paragraph("When creating tables, consider:")
        .bulleted_list(
            [
                "Keep headers concise and descriptive",
                "Use consistent data formatting within columns",
                "Consider alignment for numeric data",
                "Add visual indicators (emojis) for status/trends",
                "Limit table width for better readability",
                "Use meaningful row ordering (alphabetical, priority, etc.)",
            ]
        )
        .space()
        .callout(
            text="Pro tip: Tables work best with structured data that benefits from comparison across multiple dimensions!",
            emoji="📊",
        )
        .build()
    )


async def main():
    """Demo of adding TableElement markdown to a Notion page."""

    print("🚀 Notionary Table Element Builder Demo")
    print("=" * 42)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        print("\n🔨 Building table examples with MarkdownBuilder...")
        table_content = create_table_examples_content()

        print("📋 Content Preview:")
        print("-" * 50)
        preview = (
            table_content[:200] + "..." if len(table_content) > 200 else table_content
        )
        print(preview)
        print("-" * 50)

        print("\n📝 Adding table examples to page...")
        await page.append_markdown(table_content)

        print("\n✅ Successfully added table examples using MarkdownBuilder!")
        print(f"🌐 Visit your page: {page.url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Troubleshooting:")
        print("   • Check if the page name exists in your workspace")
        print("   • Verify your Notion API credentials")
        print("   • Ensure the page has edit permissions")


if __name__ == "__main__":
    asyncio.run(main())
