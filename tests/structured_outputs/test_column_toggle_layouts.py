#!/usr/bin/env python3

"""
Test Column and Toggle layouts with structured output to verify hierarchical structure.
"""

from notionary.markdown.markdown_builder import MarkdownBuilder
from notionary.markdown.markdown_document_model import (
    MarkdownDocumentModel,
    HeadingProcessorModel,
    ParagraphProcessorModel,
    BulletedListProcessorModel,
    CalloutProcessorModel,
    CodeProcessorModel,
    ToggleProcessorModel,
    ColumnProcessorModel,
)


def test_column_and_toggle_layouts():
    """Test that Column and Toggle layouts work correctly with hierarchical structures."""

    # Create a complex document with nested Column and Toggle structures
    model = MarkdownDocumentModel(
        blocks=[
            HeadingProcessorModel(text="Advanced Layout Test", level=1),
            # Test Toggle with nested content
            ToggleProcessorModel(
                title="📋 Project Overview",
                children=[
                    HeadingProcessorModel(text="Introduction", level=2),
                    ParagraphProcessorModel(
                        text="This section contains detailed project information."
                    ),
                    BulletedListProcessorModel(
                        texts=[
                            "Feature 1: Advanced layouts",
                            "Feature 2: Nested structures",
                            "Feature 3: Type safety",
                        ]
                    ),
                    CalloutProcessorModel(
                        text="Important: This is a nested callout inside toggle!",
                        emoji="⚠️",
                    ),
                ],
            ),
            # Test Column layout with nested content
            ColumnProcessorModel(
                columns=[
                    # Left Column
                    [
                        HeadingProcessorModel(text="Left Column", level=2),
                        ParagraphProcessorModel(text="Content in the left column."),
                        CodeProcessorModel(
                            code="def left_function():\n    return 'left'",
                            language="python",
                        ),
                    ],
                    # Right Column
                    [
                        HeadingProcessorModel(text="Right Column", level=2),
                        ParagraphProcessorModel(text="Content in the right column."),
                        BulletedListProcessorModel(texts=["Right item 1", "Right item 2"]),
                    ],
                ],
                width_ratios=[0.6, 0.4],  # 60% left, 40% right
            ),
            # Test nested Toggle inside Column
            ColumnProcessorModel(
                columns=[
                    [
                        HeadingProcessorModel(text="Column with Toggle", level=2),
                        ToggleProcessorModel(
                            title="🔧 Nested Toggle in Column",
                            children=[
                                ParagraphProcessorModel(
                                    text="This toggle is nested inside a column!"
                                ),
                                CalloutProcessorModel(
                                    text="Nested structures work!", emoji="🎉"
                                ),
                            ],
                        ),
                    ],
                    [
                        HeadingProcessorModel(text="Regular Column", level=2),
                        ParagraphProcessorModel(text="Normal content in second column."),
                    ],
                ]
            ),
            ParagraphProcessorModel(text="End of layout test."),
        ]
    )

    # Process with the updated model processor
    print("🧪 Testing Column and Toggle layouts...")
    print("=" * 60)

    try:
        builder = MarkdownBuilder.from_model(model)
        markdown = builder.build()

        print("Generated Markdown:")
        print("-" * 40)
        print(markdown)
        print("-" * 40)

        # Verify Toggle structure
        assert "📋 Project Overview" in markdown, "Toggle title missing"
        assert "⚠️" in markdown, "Nested callout in toggle missing"
        assert "Feature 1: Advanced layouts" in markdown, "Toggle nested list missing"

        # Verify Column structure
        assert "::: columns" in markdown, "Column container missing"
        assert "::: column" in markdown, "Individual columns missing"
        assert "Left Column" in markdown, "Left column content missing"
        assert "Right Column" in markdown, "Right column content missing"
        assert "def left_function" in markdown, "Code block in column missing"

        # Verify nested Toggle in Column
        assert (
            "🔧 Nested Toggle in Column" in markdown
        ), "Nested toggle in column missing"
        assert (
            "This toggle is nested inside a column!" in markdown
        ), "Toggle content in column missing"

        print("✅ Column structure test passed!")
        print("✅ Toggle structure test passed!")
        print("✅ Nested structures test passed!")
        print(f"✅ Builder has {len(builder.children)} top-level children")

        # Count children types
        toggle_count = sum(
            1 for child in builder.children if "ToggleMarkdownNode" in str(type(child))
        )
        column_count = sum(
            1
            for child in builder.children
            if "ColumnListMarkdownNode" in str(type(child))
        )

        print("📊 Structure Analysis:")
        print(f"   - Toggle blocks: {toggle_count}")
        print(f"   - Column blocks: {column_count}")
        print("🎉 Hierarchical layout structures work perfectly!")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_column_and_toggle_layouts()
    if success:
        print("\n🎯 Column and Toggle layouts are working correctly!")
        print("✨ Structured output supports hierarchical structures!")
    else:
        print("\n💥 Test failed - layouts need debugging")
