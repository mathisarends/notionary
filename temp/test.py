"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio

from pydantic import Field

from notionary import NotionPage

from notionary.schemas import NotionContentSchema
from notionary.blocks import (
    MarkdownDocumentModel,
    ParagraphMarkdownNode,
    HeadingMarkdownNode,
    BulletedListMarkdownNode
)

PAGE_NAME = "Jarvis Clipboard"

class SimpleReport(NotionContentSchema):
    """Einfacher Bericht mit Titel, Beschreibung und Punkten - hartverdrahtet für Tests"""
    
    title: str = Field(description="Report title")
    description: str = Field(description="Brief description of what this report covers")
    key_points: list[str] = Field(description="3-5 main findings or points")
    
    def to_notion_content(self) -> MarkdownDocumentModel:
        blocks = [
            HeadingMarkdownNode(text=self.title, level=1),
            ParagraphMarkdownNode(text=self.description),
            HeadingMarkdownNode(text="Key Points", level=2),
            BulletedListMarkdownNode(texts=self.key_points)
        ]
        return MarkdownDocumentModel(blocks=blocks)

async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)
        
        simple_report = SimpleReport(
            title="Test Report: Python Performance",
            description="This report covers key optimization techniques for Python applications.",
            key_points=[
                "Use list comprehensions instead of loops",
                "Profile your code with cProfile", 
                "Leverage NumPy for numerical computations",
                "Cache expensive function calls",
                "Use generators for memory efficiency"
            ]
        )
        await page.append_markdown(simple_report)

        print("✅ Successfully added all caption syntax examples!")

        content = await page.get_text_content()
        print(f"📄 Page content preview:\n{content[:500]}...")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
