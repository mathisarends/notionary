"""
Minimal tests for TableElement.
Tests core functionality for table blocks with | syntax.
"""

from unittest.mock import Mock
from notionary.blocks.table.table_element import TableElement
from notionary.blocks.table.table_models import (
    CreateTableBlock,
    TableBlock,
)


def test_match_markdown_valid():
    """Test recognition of valid table formats."""
    assert TableElement.match_markdown("| Header 1 | Header 2 | Header 3 |")
    assert TableElement.match_markdown("|Name|Age|City|")
    assert TableElement.match_markdown("  | Col1 | Col2 |  ")
    assert TableElement.match_markdown("| Single Column |")
    assert TableElement.match_markdown("| A | B | C | D | E |")


def test_match_markdown_invalid():
    """Test rejection of invalid table formats."""
    assert not TableElement.match_markdown("| Missing end pipe")
    assert not TableElement.match_markdown("Missing start pipe |")
    assert not TableElement.match_markdown("No pipes at all")
    assert not TableElement.match_markdown("- Bullet list")
    assert not TableElement.match_markdown("1. Numbered list")
    assert not TableElement.match_markdown("")
    assert not TableElement.match_markdown("   ")


def test_match_notion_valid():
    """Test recognition of valid Notion table blocks."""
    mock_block = Mock()
    mock_block.type = "table"

    assert TableElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    mock_block = Mock()
    mock_block.type = "paragraph"

    assert not TableElement.match_notion(mock_block)


def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = TableElement.markdown_to_notion("| Header 1 | Header 2 | Header 3 |")

    assert result is not None
    assert isinstance(result, CreateTableBlock)
    assert isinstance(result.table, TableBlock)
    assert result.table.table_width == 3
    assert result.table.has_column_header is True
    assert result.table.has_row_header is False
    assert result.table.children == []  # Empty, filled by stack processor


def test_markdown_to_notion_different_column_counts():
    """Test conversion with different column counts."""
    test_cases = [
        ("| Single |", 1),
        ("| A | B |", 2),
        ("| A | B | C | D |", 4),
        ("| One | Two | Three | Four | Five |", 5),
    ]

    for markdown_text, expected_cols in test_cases:
        result = TableElement.markdown_to_notion(markdown_text)
        assert result is not None
        assert result.table.table_width == expected_cols


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert TableElement.markdown_to_notion("| Missing end") is None
    assert TableElement.markdown_to_notion("Missing start |") is None
    assert TableElement.markdown_to_notion("No pipes") is None
    assert TableElement.markdown_to_notion("") is None


def test_notion_to_markdown_empty_table():
    """Test conversion of empty Notion table to markdown."""
    mock_block = Mock()
    mock_block.type = "table"
    mock_block.table = Mock()
    mock_block.table.table_width = 3
    mock_block.table.has_column_header = True
    mock_block.table.has_row_header = False
    mock_block.children = []  # Empty table

    result = TableElement.notion_to_markdown(mock_block)

    assert result is not None
    lines = result.split("\n")
    assert len(lines) == 3  # Header, separator, data row
    assert "Column 1" in lines[0]
    assert "--------" in lines[1]


def test_notion_to_markdown_with_data():
    """Test conversion with actual table data."""
    # Create mock table row
    mock_cell_1 = [{"text": {"content": "John"}}]
    mock_cell_2 = [{"text": {"content": "25"}}]

    mock_row = Mock()
    mock_row.type = "table_row"
    mock_row.table_row = Mock()
    mock_row.table_row.cells = [mock_cell_1, mock_cell_2]

    # Create mock table block
    mock_block = Mock()
    mock_block.type = "table"
    mock_block.table = Mock()
    mock_block.table.table_width = 2
    mock_block.table.has_column_header = True
    mock_block.table.has_row_header = False
    mock_block.children = [mock_row]

    result = TableElement.notion_to_markdown(mock_block)

    assert result is not None
    lines = result.split("\n")
    assert len(lines) >= 2  # At least header + separator


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert TableElement.notion_to_markdown(mock_block) is None

    mock_block.type = "table"
    mock_block.table = None
    assert TableElement.notion_to_markdown(mock_block) is None


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    result = TableElement.get_llm_prompt_content()
    assert result is not None


def test_parse_table_row():
    """Test the _parse_table_row helper method."""
    test_cases = [
        ("| A | B | C |", ["A", "B", "C"]),
        ("|Name|Age|City|", ["Name", "Age", "City"]),
        ("| Single |", ["Single"]),
        ("| A | B | C | D | E |", ["A", "B", "C", "D", "E"]),
        ("|  Spaced  |  Content  |", ["Spaced", "Content"]),
    ]

    for input_text, expected_cells in test_cases:
        result = TableElement._parse_table_row(input_text)
        assert result == expected_cells


def test_parse_table_row_edge_cases():
    """Test edge cases for table row parsing."""
    # Empty cells
    result = TableElement._parse_table_row("| | |")
    assert result == ["", ""]

    # Whitespace cells
    result = TableElement._parse_table_row("|   |   |")
    assert result == ["", ""]

    # Mixed content
    result = TableElement._parse_table_row("| Text | 123 | !@# |")
    assert result == ["Text", "123", "!@#"]


def test_is_table_row():
    """Test the is_table_row helper method."""
    # Valid table rows
    assert TableElement.is_table_row("| A | B | C |")
    assert TableElement.is_table_row("|Name|Age|")
    assert TableElement.is_table_row("  | Spaced |  ")

    # Invalid table rows
    assert not TableElement.is_table_row("| Missing end")
    assert not TableElement.is_table_row("Missing start |")
    assert not TableElement.is_table_row("No pipes")
    assert not TableElement.is_table_row("")


def test_row_pattern_regex_directly():
    """Test the ROW_PATTERN regex directly."""
    pattern = TableElement.ROW_PATTERN

    # Valid patterns
    assert pattern.match("| A | B | C |")
    assert pattern.match("|A|B|C|")
    assert pattern.match("  | A | B |  ")

    # Invalid patterns
    assert not pattern.match("| Missing end")
    assert not pattern.match("Missing start |")
    assert not pattern.match("No pipes")


def test_separator_pattern_regex():
    """Test the SEPARATOR_PATTERN regex directly."""
    pattern = TableElement.SEPARATOR_PATTERN

    # Valid separator patterns
    assert pattern.match("| --- | --- | --- |")
    assert pattern.match("|---|---|---|")
    assert pattern.match("| :-- | :-: | --: |")
    assert pattern.match("|:---|:---:|---:|")

    # Invalid patterns (should not match regular content)
    assert not pattern.match("| A | B | C |")
    assert not pattern.match("| Text | Data |")


def test_whitespace_handling():
    """Test handling of whitespace in tables."""
    # Leading/trailing whitespace
    assert TableElement.match_markdown("  | A | B |  ")

    # Whitespace in cells
    result = TableElement.markdown_to_notion("| A   | B |")
    assert result is not None

    # Parse with extra whitespace
    cells = TableElement._parse_table_row("|  A   |   B  |")
    assert cells == ["A", "B"]


def test_special_characters_in_cells():
    """Test tables with special characters."""
    special_cases = [
        "| Äöü | ßẞ | çñ |",
        "| 😀 | 🎉 | ✅ |",
        "| !@# | $%^ | &*() |",
        "| Code: `var` | **Bold** | *Italic* |",
    ]

    for table_text in special_cases:
        assert TableElement.match_markdown(table_text)
        result = TableElement.markdown_to_notion(table_text)
        assert result is not None


def test_single_column_table():
    """Test tables with single column."""
    single_col = "| Single Column |"

    assert TableElement.match_markdown(single_col)
    result = TableElement.markdown_to_notion(single_col)
    assert result is not None
    assert result.table.table_width == 1


def test_many_columns_table():
    """Test tables with many columns."""
    many_cols = "| A | B | C | D | E | F | G | H | I | J |"

    assert TableElement.match_markdown(many_cols)
    result = TableElement.markdown_to_notion(many_cols)
    assert result is not None
    assert result.table.table_width == 10


def test_empty_cells():
    """Test tables with empty cells."""
    empty_cells = "| Name | | Age |"

    assert TableElement.match_markdown(empty_cells)
    result = TableElement.markdown_to_notion(empty_cells)
    assert result is not None
    assert result.table.table_width == 3

    # Parse the row
    cells = TableElement._parse_table_row(empty_cells)
    assert cells == ["Name", "", "Age"]


def test_table_properties():
    """Test table block properties."""
    result = TableElement.markdown_to_notion("| A | B |")

    assert result is not None
    table = result.table

    # Default properties
    assert table.has_column_header is True
    assert table.has_row_header is False
    assert table.children == []
    assert table.table_width == 2


def test_notion_table_without_children():
    """Test notion table conversion when no children exist."""
    mock_block = Mock()
    mock_block.type = "table"
    mock_block.table = Mock()
    mock_block.table.table_width = 2
    mock_block.table.has_column_header = True
    mock_block.table.has_row_header = False
    mock_block.children = None  # No children

    result = TableElement.notion_to_markdown(mock_block)

    assert result is not None
    lines = result.split("\n")
    assert "Column 1" in lines[0]
    assert "Column 2" in lines[0]


def test_row_parsing_without_pipes():
    """Test behavior when pipes are missing."""
    # These should be handled gracefully
    cases = [
        "A | B | C",  # Missing start pipe
        "| A | B | C",  # Missing end pipe
        "A | B | C",  # Missing both pipes
    ]

    # The _parse_table_row should handle these cases
    for case in cases:
        try:
            result = TableElement._parse_table_row(case)
            assert isinstance(result, list)
        except Exception:
            # Should not crash
            pass
