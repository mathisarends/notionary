"""
# Notionary: Toggleable Heading Demo
===================================

Simple demo showing how to create collapsible heading sections using MarkdownBuilder.
Perfect for creating expandable document sections!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_toggleable_heading_examples() -> str:
    """Creates toggleable heading examples using MarkdownBuilder."""
    return (
        MarkdownBuilder()
        .h2("📚 Toggleable Headings")
        .paragraph("Toggleable headings create collapsible sections with proper heading hierarchy:")
        .space()
        # H2 Toggleable heading
        .toggleable_heading(
            "Project Overview",
            2,
            lambda t: t.paragraph("This section contains high-level project information.")
            .bulleted_list(
                [
                    "**Goal**: Build a scalable web application",
                    "**Timeline**: 6 months",
                    "**Budget**: $50,000",
                    "**Team Size**: 5 developers",
                ]
            )
            .callout("All deliverables must be completed by Q4 2024.", "⏰"),
        )
        .space()
        # H3 Toggleable heading with rich content
        .toggleable_heading(
            "Technical Requirements",
            3,
            lambda t: t.paragraph("Detailed technical specifications and constraints:")
            .numbered_list(
                [
                    "**Performance**: Page load time < 2 seconds",
                    "**Scalability**: Support 10,000+ concurrent users",
                    "**Security**: GDPR and SOC2 compliance",
                    "**Accessibility**: WCAG 2.1 AA standards",
                ]
            )
            .quote("Quality is not an act, it is a habit. - Aristotle"),
        )
        .space()
        # Nested structure with multiple levels
        .toggleable_heading(
            "Development Milestones",
            2,
            lambda t: t.paragraph("Major milestones organized by development phase:")
            .toggleable_heading(
                "Frontend Development",
                3,
                lambda inner: inner.bulleted_list(
                    [
                        "React component library setup",
                        "Responsive design implementation",
                        "State management with Redux",
                        "Unit test coverage > 80%",
                    ]
                ).paragraph("*Estimated completion: 8 weeks*"),
            )
            .toggleable_heading(
                "Backend Development",
                3,
                lambda inner: inner.bulleted_list(
                    [
                        "RESTful API design and implementation",
                        "Database schema optimization",
                        "Authentication and authorization",
                        "API documentation with Swagger",
                    ]
                ).paragraph("*Estimated completion: 10 weeks*"),
            )
            .toggleable_heading(
                "DevOps & Deployment",
                3,
                lambda inner: inner.bulleted_list(
                    [
                        "CI/CD pipeline setup",
                        "Docker containerization",
                        "AWS infrastructure provisioning",
                        "Monitoring and logging setup",
                    ]
                ).paragraph("*Estimated completion: 4 weeks*"),
            ),
        )
        .divider()
        .callout(
            "Toggleable headings are perfect for creating structured documents that maintain readability!",
            "📖",
        )
        .build()
    )


async def main():
    """Demo of adding toggleable heading elements to a Notion page."""

    print("🚀 Notionary Toggleable Heading Demo")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_title(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"└── URL: {page.url}")

        print("\n📝 Creating toggleable heading examples...")
        content = create_toggleable_heading_examples()

        print("✨ Adding content to page...")
        await page.append_markdown(content)

        print("\n✅ Successfully added toggleable heading examples!")
        print(f"🌐 View at: {page.url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
