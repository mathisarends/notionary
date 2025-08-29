"""
# Notionary: Toggle Element Demo
===============================

Simple demo showing how to create collapsible toggle elements using MarkdownBuilder.
Perfect for organizing content that can be expanded/collapsed!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_toggle_examples() -> str:
    """Creates toggle examples using MarkdownBuilder."""
    return (
        MarkdownBuilder()
        .h2("🔽 Toggle Elements")
        .paragraph("Toggles help organize content that can be shown/hidden:")
        .space()
        
        # Simple toggle
        .toggle(
            "Click to expand project details",
            lambda t: t
            .paragraph("This project focuses on building a modern web application.")
            .bulleted_list([
                "React frontend with TypeScript",
                "Node.js backend with Express",
                "PostgreSQL database",
                "Docker containerization"
            ])
        )
        .space()
        
        # Toggle with rich content
        .toggle(
            "Team Information",
            lambda t: t
            .paragraph("Our development team consists of:")
            .numbered_list([
                "**Sarah** - Frontend Developer",
                "**Mike** - Backend Developer", 
                "**Lisa** - UI/UX Designer",
                "*Alex* - DevOps Engineer"
            ])
            .callout("All team members work remotely across different time zones.", "🌍")
        )
        .space()
        
        # Nested toggles
        .toggle(
            "Development Phases",
            lambda t: t
            .paragraph("The project is divided into several phases:")
            .toggle(
                "Phase 1: Planning",
                lambda inner: inner
                .bulleted_list([
                    "Requirements gathering",
                    "Technical architecture",
                    "Team allocation"
                ])
            )
            .toggle(
                "Phase 2: Development",
                lambda inner: inner
                .bulleted_list([
                    "Frontend implementation",
                    "Backend API development",
                    "Database design"
                ])
            )
            .toggle(
                "Phase 3: Testing & Deployment",
                lambda inner: inner
                .bulleted_list([
                    "Unit and integration testing",
                    "Performance optimization",
                    "Production deployment"
                ])
            )
        )
        .divider()
        .callout(
            "Pro tip: Use toggles to keep pages clean while providing detailed information on demand!",
            "💡"
        )
        .build()
    )


async def main():
    """Demo of adding toggle elements to a Notion page."""
    
    print("🚀 Notionary Toggle Element Demo")
    print("=" * 35)
    
    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)
        
        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"└── URL: {page.url}")
        
        print("\n📝 Creating toggle examples...")
        content = create_toggle_examples()
        
        print("✨ Adding content to page...")
        await page.append_markdown(content)
        
        print("\n✅ Successfully added toggle examples!")
        print(f"🌐 View at: {page.url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
