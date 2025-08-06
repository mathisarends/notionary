"""
Minimal tests for TableElement.
Tests core functionality for markdown tables (| Header |).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.table import TableElement
from notionary.blocks.table.table_models import CreateTableBlock, TableBlock


def test_match_markdown_valid():
    """Test recognition of valid table row formats."""
    assert TableElement.match_markdown("| Header 1 | Header 2 |")
    assert TableElement.match_markdown("| Cell A | Cell B | Cell C |")
    assert TableElement.match_markdown("  | Indented | Table |  ")
    assert TableElement.match_markdown("| Single |")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not TableElement.match_markdown("Regular text")
    assert not TableElement.match_markdown("| No closing pipe")
    assert not TableElement.match_markdown("No opening pipe |")
    assert not TableElement.match_markdown("||")  # Empty
    assert not TableElement.match_markdown("")


def test_match_notion():
    """Test recognition of Notion table blocks."""
    # Valid table block
    table_block = Mock()
    table_block.type = "table"
    assert TableElement.match_notion(table_block)

    # Invalid blocks
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    assert not TableElement.match_notion(paragraph_block)


def test_markdown_to_notion():
    """Test conversion from markdown table header to Notion."""
    result = TableElement.markdown_to_notion("| Name | Age | City |")

    assert result is not None
    assert isinstance(result, CreateTableBlock)
    assert result.type == "table"
    assert isinstance(result.table, TableBlock)
    assert result.table.table_width == 3  # 3 columns
    assert result.table.has_column_header is True
    assert result.table.has_row_header is False
    assert result.table.children == []  # Empty, filled by stack processor


def test_markdown_to_notion_different_column_counts():
    """Test tables with different column counts."""
    test_cases = [
        ("| Single |", 1),
        ("| A | B |", 2),
        ("| A | B | C | D |", 4),
        ("| A | B | C | D | E | F |", 6),
    ]

    for markdown, expected_width in test_cases:
        result = TableElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.table.table_width == expected_width


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert TableElement.markdown_to_notion("Regular text") is None
    assert TableElement.markdown_to_notion("| No closing") is None
    assert TableElement.markdown_to_notion("No opening |") is None


def test_notion_to_markdown_empty_table():
    """Test conversion of empty Notion table to markdown."""
    # Mock empty table block
    block = Mock()
    block.type = "table"
    block.table = Mock()
    block.table.table_width = 3
    block.table.has_column_header = True
    block.children = []  # Empty table

    result = TableElement.notion_to_markdown(block)
    expected = (
        "| Column 1 | Column 2 | Column 3 |\n"
        "| -------- | -------- | -------- |\n"
        "| " + " " * 8 + " | " + " " * 8 + " | " + " " * 8 + " |"
    )
    assert result == expected


def test_notion_to_markdown_with_data():
    """Test conversion of Notion table with data to markdown."""
    # Mock table block with children
    block = Mock()
    block.type = "table"
    block.table = Mock()
    block.table.table_width = 2
    block.table.has_column_header = True

    # Mock table rows
    header_row = Mock()
    header_row.type = "table_row"
    header_row.table_row = Mock()
    header_row.table_row.cells = [["Name"], ["Age"]]  # Cell content as list

    data_row = Mock()
    data_row.type = "table_row"
    data_row.table_row = Mock()
    data_row.table_row.cells = [["Alice"], ["30"]]

    block.children = [header_row, data_row]

    result = TableElement.notion_to_markdown(block)
    expected_lines = ["| Name | Age |", "| -------- | -------- |", "| Alice | 30 |"]
    assert result == "\n".join(expected_lines)


def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    assert TableElement.notion_to_markdown(paragraph_block) is None

    # No table property
    table_block = Mock()
    table_block.type = "table"
    table_block.table = None
    assert TableElement.notion_to_markdown(table_block) is None


def test_parse_table_row():
    """Test parsing table row into cells."""
    test_cases = [
        ("| A | B | C |", ["A", "B", "C"]),
        ("| Single |", ["Single"]),
        ("| Left | Middle | Right |", ["Left", "Middle", "Right"]),
        ("|  Spaces  |  Around  |", ["Spaces", "Around"]),
    ]

    for row_text, expected_cells in test_cases:
        result = TableElement._parse_table_row(row_text)
        assert result == expected_cells


def test_is_table_row():
    """Test table row recognition helper."""
    assert TableElement.is_table_row("| Valid | Row |")
    assert TableElement.is_table_row("  | Indented | Row |  ")
    assert not TableElement.is_table_row("Regular text")
    assert not TableElement.is_table_row("| No closing")


@pytest.mark.parametrize(
    "markdown,should_match,expected_width",
    [
        ("| A | B |", True, 2),
        ("| A | B | C |", True, 3),
        ("| Single |", True, 1),
        ("  | A | B |  ", True, 2),  # With whitespace
        ("Regular text", False, None),
        ("| No closing", False, None),
        ("No opening |", False, None),
        ("", False, None),
    ],
)
def test_markdown_patterns(markdown, should_match, expected_width):
    """Test various markdown patterns."""
    # Test matching
    result = TableElement.match_markdown(markdown)
    assert result == should_match

    # Test conversion if it should match
    if should_match:
        notion_result = TableElement.markdown_to_notion(markdown)
        assert notion_result is not None
        assert notion_result.table.table_width == expected_width


def test_row_patterns():
    """Test the regex patterns directly."""
    # Test ROW_PATTERN
    assert TableElement.ROW_PATTERN.match("| Cell 1 | Cell 2 |")
    assert TableElement.ROW_PATTERN.match("  | A | B |  ")
    assert not TableElement.ROW_PATTERN.match("Not a table row")

    # Test SEPARATOR_PATTERN
    assert TableElement.SEPARATOR_PATTERN.match("| -------- | -------- |")
    assert TableElement.SEPARATOR_PATTERN.match("| --- | --- |")
    assert TableElement.SEPARATOR_PATTERN.match("| :--- | ---: |")  # Alignment
    assert not TableElement.SEPARATOR_PATTERN.match("| Cell | Cell |")


def test_table_properties():
    """Test that created tables have correct properties."""
    result = TableElement.markdown_to_notion("| A | B | C |")

    assert result is not None
    table = result.table
    assert table.table_width == 3
    assert table.has_column_header is True
    assert table.has_row_header is False
    assert table.children == []  # Empty for stack processor


def test_cell_parsing_edge_cases():
    """Test cell parsing with edge cases."""
    edge_cases = [
        ("| |", [""]),  # Empty cell
        ("|| A ||", ["", " A ", ""]),  # Multiple pipes
        ("|  Lots  of   spaces  |", ["Lots  of   spaces"]),  # Multiple spaces
        ("| Special: äöü 🚀 |", ["Special: äöü 🚀"]),  # Unicode
    ]

    for row_text, expected_cells in edge_cases:
        result = TableElement._parse_table_row(row_text)
        assert result == expected_cells


def test_empty_table_fallback():
    """Test fallback for empty tables."""
    widths_to_test = [1, 2, 3, 5]

    for width in widths_to_test:
        block = Mock()
        block.type = "table"
        block.table = Mock()
        block.table.table_width = width
        block.table.has_column_header = True
        block.children = []

        result = TableElement.notion_to_markdown(block)
        lines = result.split("\n")

        # Should have header, separator, and data row
        assert len(lines) == 3

        # Count columns in header
        header_cols = lines[0].count("|") - 1  # -1 because of leading/trailing |
        assert header_cols == width


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = TableElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, "syntax")
    assert "|" in content.syntax
    assert "table" in content.syntax.lower() or "header" in content.syntax.lower()
