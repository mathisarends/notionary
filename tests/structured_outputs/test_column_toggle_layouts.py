#!/usr/bin/env python3

"""
Test Column and Toggle layouts with structured output to verify hierarchical structure.
"""

import pytest
from notionary.markdown.markdown_builder import MarkdownBuilder
from notionary.markdown.markdown_document_model import MarkdownDocumentModel
from notionary.blocks.heading import HeadingMarkdownNode
from notionary.blocks.paragraph import ParagraphMarkdownNode
from notionary.blocks.bulleted_list import BulletedListMarkdownNode
from notionary.blocks.callout import CalloutMarkdownNode
from notionary.blocks.code import CodeMarkdownNode
from notionary.blocks.toggle import ToggleMarkdownNode
from notionary.blocks.column import ColumnMarkdownNode, ColumnListMarkdownNode


class TestColumnToggleLayouts:
    """Test suite for Column and Toggle layout structures."""

    @pytest.fixture
    def complex_model(self):
        """Create a complex document model with nested structures."""
        return MarkdownDocumentModel(
            blocks=[
                HeadingMarkdownNode(text="Advanced Layout Test", level=1),
                # Test Toggle with nested content
                ToggleMarkdownNode(
                    title="📋 Project Overview",
                    children=[
                        HeadingMarkdownNode(text="Introduction", level=2),
                        ParagraphMarkdownNode(
                            text="This section contains detailed project information."
                        ),
                        BulletedListMarkdownNode(
                            texts=[
                                "Feature 1: Advanced layouts",
                                "Feature 2: Nested structures",
                                "Feature 3: Type safety",
                            ]
                        ),
                        CalloutMarkdownNode(
                            text="Important: This is a nested callout inside toggle!",
                            emoji="⚠️",
                        ),
                    ],
                ),
                # Test Column layout with nested content
                ColumnListMarkdownNode(
                    columns=[
                        # Left Column
                        ColumnMarkdownNode(
                            children=[
                                HeadingMarkdownNode(text="Left Column", level=2),
                                ParagraphMarkdownNode(text="Content in the left column."),
                                CodeMarkdownNode(
                                    code="def left_function():\n    return 'left'",
                                    language="python",
                                ),
                            ],
                            width_ratio=0.6,
                        ),
                        # Right Column
                        ColumnMarkdownNode(
                            children=[
                                HeadingMarkdownNode(text="Right Column", level=2),
                                ParagraphMarkdownNode(text="Content in the right column."),
                                BulletedListMarkdownNode(texts=["Right item 1", "Right item 2"]),
                            ],
                            width_ratio=0.4,
                        ),
                    ]
                ),
                # Test nested Toggle inside Column
                ColumnListMarkdownNode(
                    columns=[
                        ColumnMarkdownNode(
                            children=[
                                HeadingMarkdownNode(text="Column with Toggle", level=2),
                                ToggleMarkdownNode(
                                    title="🔧 Nested Toggle in Column",
                                    children=[
                                        ParagraphMarkdownNode(
                                            text="This toggle is nested inside a column!"
                                        ),
                                        CalloutMarkdownNode(
                                            text="Nested structures work!", emoji="🎉"
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        ColumnMarkdownNode(
                            children=[
                                HeadingMarkdownNode(text="Regular Column", level=2),
                                ParagraphMarkdownNode(text="Normal content in second column."),
                            ]
                        ),
                    ]
                ),
                ParagraphMarkdownNode(text="End of layout test."),
            ]
        )

    def test_toggle_structure(self, complex_model):
        """Test that toggle blocks are generated correctly."""
        builder = MarkdownBuilder.from_model(complex_model)
        markdown = builder.build()

        # Check main toggle
        assert "+++ 📋 Project Overview" in markdown, "Main toggle title missing"
        assert "## Introduction" in markdown, "Toggle heading missing"
        assert "Feature 1: Advanced layouts" in markdown, "Toggle list item missing"
        assert '[callout](Important: This is a nested callout inside toggle! "⚠️")' in markdown, "Toggle callout missing"

    def test_column_structure(self, complex_model):
        """Test that column blocks are generated correctly."""
        builder = MarkdownBuilder.from_model(complex_model)
        markdown = builder.build()

        # Check column containers
        assert "::: columns" in markdown, "Column container missing"
        assert "::: column 0.6" in markdown, "Left column with width missing"
        assert "::: column 0.4" in markdown, "Right column with width missing"

        # Check column content
        assert "## Left Column" in markdown, "Left column heading missing"
        assert "## Right Column" in markdown, "Right column heading missing"
        assert "def left_function" in markdown, "Code in left column missing"
        assert "Right item 1" in markdown, "List item in right column missing"

    def test_nested_toggle_in_column(self, complex_model):
        """Test that nested toggle inside column works."""
        builder = MarkdownBuilder.from_model(complex_model)
        markdown = builder.build()

        # Check nested toggle
        assert "+++ 🔧 Nested Toggle in Column" in markdown, "Nested toggle title missing"
        assert "This toggle is nested inside a column!" in markdown, "Nested toggle content missing"
        assert '[callout](Nested structures work! "🎉")' in markdown, "Nested callout missing"

    def test_builder_structure_analysis(self, complex_model):
        """Test the structure analysis of the builder."""
        builder = MarkdownBuilder.from_model(complex_model)

        # Count children types
        toggle_count = sum(
            1 for child in builder.children if "ToggleMarkdownNode" in str(type(child))
        )
        column_count = sum(
            1
            for child in builder.children
            if "ColumnListMarkdownNode" in str(type(child))
        )

        assert toggle_count == 1, f"Expected 1 toggle, got {toggle_count}"
        assert column_count == 2, f"Expected 2 column lists, got {column_count}"
        assert len(builder.children) == 5, f"Expected 5 top-level children, got {len(builder.children)}"

    def test_overall_markdown_generation(self, complex_model):
        """Test the complete markdown generation."""
        builder = MarkdownBuilder.from_model(complex_model)
        markdown = builder.build()

        # Check overall structure
        assert "# Advanced Layout Test" in markdown, "Main heading missing"
        assert "End of layout test." in markdown, "Final paragraph missing"

        # Ensure proper markdown formatting
        lines = markdown.split('\n')
        assert lines[0] == "# Advanced Layout Test", "First line should be main heading"
        assert lines[-1] == "End of layout test.", "Last line should be final paragraph"

    def test_markdown_syntax_compliance(self, complex_model):
        """Test that generated markdown follows proper syntax rules."""
        builder = MarkdownBuilder.from_model(complex_model)
        markdown = builder.build()

        # Count opening and closing markers correctly
        toggle_openings = markdown.count("+++ ")
        toggle_closings = markdown.count("+++") - toggle_openings  # Total +++ minus openings

        column_openings = markdown.count("::: columns")
        column_closings = markdown.count(":::") - column_openings - markdown.count("::: column")  # Total ::: minus openings and column starts

        # Each toggle should have opening and closing
        assert toggle_openings == toggle_closings, f"Toggle markers unbalanced: {toggle_openings} open, {toggle_closings} close"

        # Each column list should have proper structure
        assert column_openings == 2, f"Expected 2 column lists, got {column_openings}"

        # Each column list has 2 closings: one for each column + one for the list itself
        expected_closings = column_openings * 2
        assert column_closings == expected_closings, f"Column markers unbalanced: {column_openings} open, {column_closings} close (expected {expected_closings})"
