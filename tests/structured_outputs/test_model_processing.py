#!/usr/bin/env python3

"""
Test the refactored MarkdownBuilder and MarkdownModelProcessor separation.
"""

from notionary.markdown.markdown_builder import MarkdownBuilder
from notionary.markdown.markdown_document_model import MarkdownDocumentModel
from notionary.blocks.heading import HeadingMarkdownNode
from notionary.blocks.paragraph import ParagraphMarkdownNode
from notionary.blocks.bulleted_list import BulletedListMarkdownNode
from notionary.blocks.callout import CalloutMarkdownNode
from notionary.blocks.code import CodeMarkdownNode
from notionary.blocks.divider import DividerMarkdownNode
from notionary.blocks.todo import TodoMarkdownNode


def test_refactored_model_processing():
    """Test that the model processing still works after refactoring."""

    # Create a simple document model with the new simplified API
    model = MarkdownDocumentModel(
        blocks=[
            HeadingMarkdownNode(text="Test Document", level=1),
            ParagraphMarkdownNode(text="This is a test paragraph."),
            HeadingMarkdownNode(text="Section 2", level=2),
            ParagraphMarkdownNode(text="Another paragraph in section 2."),
            # Test more block types with simplified API
            BulletedListMarkdownNode(texts=["Item 1", "Item 2", "Item 3"]),
            CalloutMarkdownNode(text="Important note!", emoji="⚠️"),
            CodeMarkdownNode(code="print('Hello World')", language="python"),
            DividerMarkdownNode(),
            TodoMarkdownNode(text="Complete refactoring", checked=True),
        ]
    )

    # Test the from_model class method
    builder = MarkdownBuilder.from_model(model)
    markdown = builder.build()

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

    print("✅ Simplified API refactoring successful!")
    print(f"✅ Builder has {len(builder.children)} children")
    print("✅ All assertions passed!")
    print("🎉 No more params wrapper needed!")


if __name__ == "__main__":
    test_refactored_model_processing()
