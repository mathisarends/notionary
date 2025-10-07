import pytest
from pydantic import Field

from notionary.blocks.markdown.builder import MarkdownBuilder
from notionary.schemas import NotionContentSchema


class TestColumnToggleLayouts:
    """Test suite for Column and Toggle layout structures."""

    @pytest.fixture
    def complex_schema(self):
        """Create a complex schema with nested structures using the new builder API."""

        class ComplexLayoutSchema(NotionContentSchema):
            """Schema that generates complex layouts with toggles and columns"""

            title: str = Field(default="Advanced Layout Test")
            project_features: list[str] = Field(
                default=[
                    "Feature 1: Advanced layouts",
                    "Feature 2: Nested structures",
                    "Feature 3: Type safety",
                ]
            )

            def to_notion_content(self, builder: MarkdownBuilder) -> str:
                return (
                    builder.h1(self.title)
                    # Test Toggle with nested content
                    .toggle(
                        "📋 Project Overview",
                        lambda t: t.h2("Introduction")
                        .paragraph("This section contains detailed project information.")
                        .bulleted_list(self.project_features)
                        .callout("Important: This is a nested callout inside toggle!", "⚠️"),
                    )
                    # Test Column layout with nested content
                    .columns(
                        # Left Column
                        lambda col: col.h2("Left Column")
                        .paragraph("Content in the left column.")
                        .code("def left_function():\n    return 'left'", "python"),
                        # Right Column
                        lambda col: col.h2("Right Column")
                        .paragraph("Content in the right column.")
                        .bulleted_list(["Right item 1", "Right item 2"]),
                        width_ratios=[0.6, 0.4],
                    )
                    # Test nested Toggle inside Column
                    .columns(
                        lambda col: col.h2("Column with Toggle").toggle(
                            "🔧 Nested Toggle in Column",
                            lambda t: t.paragraph("This toggle is nested inside a column!").callout(
                                "Nested structures work!", "🎉"
                            ),
                        ),
                        lambda col: col.h2("Regular Column").paragraph("Normal content in second column."),
                    )
                    .paragraph("End of layout test.")
                    .build()
                )

        return ComplexLayoutSchema()

    def test_toggle_structure(self, complex_schema):
        """Test that toggle blocks are generated correctly."""
        builder = MarkdownBuilder()
        markdown = complex_schema.to_notion_content(builder)

        # Check main toggle
        assert "+++ 📋 Project Overview" in markdown, "Main toggle title missing"
        assert "## Introduction" in markdown, "Toggle heading missing"
        assert "Feature 1: Advanced layouts" in markdown, "Toggle list item missing"
        assert "::: callout ⚠️" in markdown, "Toggle callout missing"
        assert "Important: This is a nested callout inside toggle!" in markdown, "Toggle callout text missing"

    def test_column_structure(self, complex_schema):
        """Test that column blocks are generated correctly."""
        builder = MarkdownBuilder()
        markdown = complex_schema.to_notion_content(builder)

        # Check column containers
        assert "::: columns" in markdown, "Column container missing"
        assert "::: column 0.6" in markdown, "Left column with width missing"
        assert "::: column 0.4" in markdown, "Right column with width missing"

        # Check column content
        assert "## Left Column" in markdown, "Left column heading missing"
        assert "## Right Column" in markdown, "Right column heading missing"
        assert "def left_function" in markdown, "Code in left column missing"
        assert "Right item 1" in markdown, "List item in right column missing"

    def test_nested_toggle_in_column(self, complex_schema):
        """Test that nested toggle inside column works."""
        builder = MarkdownBuilder()
        markdown = complex_schema.to_notion_content(builder)

        # Check nested toggle
        assert "+++ 🔧 Nested Toggle in Column" in markdown, "Nested toggle title missing"
        assert "This toggle is nested inside a column!" in markdown, "Nested toggle content missing"
        assert "::: callout 🎉" in markdown, "Nested callout missing"
        assert "Nested structures work!" in markdown, "Nested callout text missing"

    def test_builder_structure_analysis(self, complex_schema):
        """Test the structure analysis of the builder."""
        builder = MarkdownBuilder()
        markdown = complex_schema.to_notion_content(builder)

        # Test that content is generated correctly
        assert "# Advanced Layout Test" in markdown, "Main heading missing"
        assert "+++ 📋 Project Overview" in markdown, "Toggle title missing"
        assert "::: columns" in markdown, "Column structure missing"

    def test_overall_markdown_generation(self, complex_schema):
        builder = MarkdownBuilder()
        markdown = complex_schema.to_notion_content(builder)

        # Check overall structure
        assert "# Advanced Layout Test" in markdown, "Main heading missing"
        assert "End of layout test." in markdown, "Final paragraph missing"

        # Ensure proper markdown formatting
        lines = markdown.split("\n")
        assert lines[0] == "# Advanced Layout Test", "First line should be main heading"
        assert lines[-1] == "End of layout test.", "Last line should be final paragraph"

    def test_markdown_syntax_compliance(self, complex_schema):
        """Test that generated markdown follows proper syntax rules."""
        builder = MarkdownBuilder()
        markdown = complex_schema.to_notion_content(builder)

        # Count opening and closing markers correctly
        toggle_openings = markdown.count("+++ ")
        toggle_closings = markdown.count("+++") - toggle_openings  # Total +++ minus openings

        column_openings = markdown.count("::: columns")
        # Count only ::: column openings (followed by space or newline)
        # Split by lines and count lines that start with "::: column"
        lines = markdown.split("\n")
        column_markers = sum(1 for line in lines if line.strip().startswith("::: column"))

        # Count ::: callout markers (these have their own closing :::)
        callout_openings = markdown.count("::: callout")

        # Total ::: minus all opening markers = closing markers
        total_triple_colons = markdown.count(":::")
        # All standalone ::: (not part of an opening)
        column_closings = total_triple_colons - column_openings - column_markers - callout_openings

        # Each toggle should have opening and closing
        assert toggle_openings == toggle_closings, (
            f"Toggle markers unbalanced: {toggle_openings} open, {toggle_closings} close"
        )

        # Each column list should have proper structure
        assert column_openings == 2, f"Expected 2 column lists, got {column_openings}"

        # Each column list should have matching closing markers
        # Structure: ::: columns, ::: column, ::: (close column), ::: column, ::: (close column), ::: (close columns)
        # So we have: openings (columns + columns) and closings (columns + column*2)
        # The closing count should be: column_openings (for each ::: columns) + column_markers (for each ::: column)
        expected_closings = column_openings + column_markers + callout_openings
        assert column_closings == expected_closings, (
            f"Column markers unbalanced: {column_openings} open, {column_closings} close (expected {expected_closings})"
        )
