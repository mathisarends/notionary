"""
# Notionary: Callout Element Markdown Demo
==========================================

A demo showing how to add custom callout elements to Notion pages using MarkdownBuilder.
Perfect for demonstrating CalloutElement syntax with the fluent interface!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_callout_examples_content() -> str:
    """Creates callout examples using the fluent MarkdownBuilder interface."""

    return (
        MarkdownBuilder()
        # Main heading
        .h2("📢 Callout Element Examples")
        .paragraph(
            "Callouts are perfect for highlighting important information, tips, warnings, and notes."
        )
        .space()
        # Default callout (uses 💡 emoji automatically)
        .h3("Default Callout")
        .callout("This is a default callout with the light bulb emoji")
        .space()
        # Information callouts
        .h3("Information & Tips")
        .callout(
            text="This is a callout with a bell emoji for notifications", emoji="🔔"
        )
        .space()
        .callout(text="Tip: Add emoji that matches your content's purpose", emoji="💡")
        .space()
        # Warning callouts
        .h3("Warnings & Alerts")
        .callout(
            text="Warning: This is an important note to pay attention to", emoji="⚠️"
        )
        .space()
        .callout(text="Critical: Immediate action required", emoji="🚨")
        .space()
        # Success callouts
        .h3("Success & Completion")
        .callout(text="Success: Your operation completed successfully", emoji="✅")
        .space()
        .callout(text="Task completed: All files have been processed", emoji="🎉")
        .space()
        # Documentation callouts
        .h3("Documentation & Notes")
        .callout(text="Note: Remember to save your work frequently", emoji="📝")
        .space()
        .callout(
            text="Documentation: This feature requires API version 2.0 or higher",
            emoji="📚",
        )
        .divider()
        # Usage guidelines
        .h3("💡 Usage Guidelines")
        .paragraph("When choosing callout types, consider:")
        .bulleted_list(
            [
                "Use 💡 for tips and helpful information",
                "Use ⚠️ for warnings and cautions",
                "Use 🚨 for critical alerts requiring immediate attention",
                "Use ✅ for success messages and confirmations",
                "Use 📝 for notes and additional context",
                "Use 🔔 for notifications and announcements",
            ]
        )
        .space()
        .callout(
            text="Pro tip: Consistent emoji usage creates better user experience and visual hierarchy!",
            emoji="🎯",
        )
        .build()
    )


async def main():
    """Demo of adding CalloutElement markdown to a Notion page."""

    print("🚀 Notionary Callout Element Builder Demo")
    print("=" * 44)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        print("\n🔨 Building callout examples with MarkdownBuilder...")
        callout_content = create_callout_examples_content()

        print("📋 Content Preview:")
        print("-" * 50)
        preview = (
            callout_content[:200] + "..."
            if len(callout_content) > 200
            else callout_content
        )
        print(preview)
        print("-" * 50)

        print("\n📝 Adding callout examples to page...")
        await page.append_markdown(callout_content)

        print("\n✅ Successfully added callout examples using MarkdownBuilder!")
        print("🌐 Visit your page: {page.url}")

    except Exception as e:
        print("❌ Error: {e}")
        print("💡 Troubleshooting:")
        print("   • Check if the page name exists in your workspace")
        print("   • Verify your Notion API credentials")
        print("   • Ensure the page has edit permissions")


if __name__ == "__main__":
    asyncio.run(main())
