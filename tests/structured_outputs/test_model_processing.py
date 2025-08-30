#!/usr/bin/env python3

"""
Test the refactored MarkdownBuilder with NotionContentSchema.
"""

from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.schemas import NotionContentSchema
from pydantic import Field


def test_refactored_model_processing():
    """Test that the schema processing works with the new builder injection API."""

    class TestDocument(NotionContentSchema):
        """Test schema with various block types."""
        
        title: str = Field(default="Test Document")
        section_title: str = Field(default="Section 2")
        list_items: list[str] = Field(default=["Item 1", "Item 2", "Item 3"])
        
        def to_notion_content(self, builder: MarkdownBuilder) -> str:
            return (builder
                .h1(self.title)
                .paragraph("This is a test paragraph.")
                .h2(self.section_title)
                .paragraph("Another paragraph in section 2.")
                .bulleted_list(self.list_items)
                .callout("Important note!", "⚠️")
                .code("print('Hello World')", "python")
                .divider()
                .todo("Complete refactoring", checked=True)
                .build()
            )

    # Create and test the schema
    document = TestDocument()
    builder = MarkdownBuilder()
    markdown = document.to_notion_content(builder)

    print("Generated Markdown:")
    print("=" * 50)
    print(markdown)
    print("=" * 50)

    # Verify structure
    assert "# Test Document" in markdown
    assert "This is a test paragraph." in markdown
    assert "## Section 2" in markdown
    assert "Another paragraph in section 2." in markdown
    assert "- Item 1" in markdown
    assert "⚠️" in markdown
    assert "```python" in markdown
    assert "print('Hello World')" in markdown
    assert "---" in markdown
    assert "[x] Complete refactoring" in markdown

    print("✅ Schema-based API refactoring successful!")
    print(f"✅ Generated markdown with {len(markdown.split('\\n'))} lines")
    print("✅ All assertions passed!")
    print("🎉 Builder injection pattern working perfectly!")


if __name__ == "__main__":
    test_refactored_model_processing()
