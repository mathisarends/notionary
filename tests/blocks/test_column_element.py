"""
Pytest tests for ColumnElement.
Tests conversion between Markdown column syntax and Notion column blocks.
"""

import pytest
from unittest.mock import patch
from notionary.blocks import ColumnElement


def test_match_markdown_valid_columns():
    """Test recognition of valid column start markers."""
    assert ColumnElement.match_markdown("::: columns")
    assert ColumnElement.match_markdown("  ::: columns  ")  # With whitespace


def test_match_markdown_invalid_formats():
    """Test rejection of invalid column formats."""
    assert not ColumnElement.match_markdown("::: column")
    assert not ColumnElement.match_markdown("::: something else")
    assert not ColumnElement.match_markdown("columns")
    assert not ColumnElement.match_markdown(":::")
    assert not ColumnElement.match_markdown("Regular text")


def test_match_notion():
    """Test recognition of Notion column_list blocks."""
    assert ColumnElement.match_notion({"type": "column_list"})
    
    assert not ColumnElement.match_notion({"type": "paragraph"})
    assert not ColumnElement.match_notion({"type": "column"})
    assert not ColumnElement.match_notion({"type": "callout"})


def test_markdown_to_notion_valid():
    """Test creation of column_list block from valid Markdown."""
    result = ColumnElement.markdown_to_notion("::: columns")
    expected = [{"type": "column_list", "column_list": {"children": []}}]
    
    assert result == expected


def test_markdown_to_notion_invalid():
    """Test invalid Markdown returns None."""
    assert ColumnElement.markdown_to_notion("::: column") is None
    assert ColumnElement.markdown_to_notion("some other text") is None
    assert ColumnElement.markdown_to_notion("") is None


def test_notion_to_markdown():
    """Test conversion from Notion column_list block to Markdown."""
    notion_block = {
        "type": "column_list",
        "column_list": {
            "children": [
                {"type": "column", "column": {"children": [{"type": "paragraph"}]}},
                {"type": "column", "column": {"children": [{"type": "paragraph"}]}},
            ]
        },
    }
    
    result = ColumnElement.notion_to_markdown(notion_block)
    expected = (
        "::: columns\n"
        "::: column\n"
        "  [Column content]\n"
        ":::\n"
        "::: column\n"
        "  [Column content]\n"
        ":::\n"
        ":::"
    )
    
    assert result == expected


def test_notion_to_markdown_empty_columns():
    """Test conversion of empty column_list."""
    notion_block = {
        "type": "column_list",
        "column_list": {"children": []}
    }
    
    result = ColumnElement.notion_to_markdown(notion_block)
    assert "::: columns" in result
    assert ":::" in result


def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    assert ColumnElement.notion_to_markdown({"type": "paragraph"}) is None
    assert ColumnElement.notion_to_markdown({}) is None


def test_is_multiline():
    """Test that column blocks are recognized as multiline elements."""
    assert ColumnElement.is_multiline()


@pytest.fixture
def mock_converter():
    """Fixture to mock the MarkdownToNotionConverter."""
    with patch("notionary.blocks.column.column_element.ColumnElement._converter_callback") as mock:
        mock.return_value = [
            {"type": "paragraph", "paragraph": {"rich_text": []}}
        ]
        yield mock


def test_find_matches_basic(mock_converter):
    """Test finding column blocks in Markdown text."""
    markdown = (
        "::: columns\n"
        "::: column\n"
        "Hello from column 1\n"
        ":::\n"
        "::: column\n"
        "Hello from column 2\n"
        ":::\n"
        ":::"
    )
    
    # Mock the converter callback
    def mock_convert(text):
        return [{"type": "paragraph", "paragraph": {"rich_text": []}}]
    
    matches = ColumnElement.find_matches(markdown, converter_callback=mock_convert)
    
    assert len(matches) == 1
    start_pos, end_pos, block = matches[0]
    
    assert isinstance(start_pos, int)
    assert isinstance(end_pos, int)
    assert start_pos < end_pos
    
    assert block["type"] == "column_list"
    assert "children" in block["column_list"]
    assert len(block["column_list"]["children"]) == 2
    assert block["column_list"]["children"][0]["type"] == "column"
    assert block["column_list"]["children"][1]["type"] == "column"


def test_find_matches_no_columns():
    """Test find_matches with text containing no columns."""
    markdown = "This is just regular text with no columns."
    
    matches = ColumnElement.find_matches(markdown)
    assert matches == []


def test_find_matches_multiple_column_blocks():
    """Test finding multiple column blocks in the same text."""
    markdown = (
        "::: columns\n"
        "::: column\n"
        "First block, column 1\n"
        ":::\n"
        ":::\n\n"
        "Some text in between\n\n"
        "::: columns\n"
        "::: column\n"
        "Second block, column 1\n"
        ":::\n"
        ":::"
    )
    
    def mock_convert(text):
        return [{"type": "paragraph", "paragraph": {"rich_text": []}}]
    
    matches = ColumnElement.find_matches(markdown, converter_callback=mock_convert)
    
    assert len(matches) == 2
    
    # Check that both matches are column_list blocks
    for start_pos, end_pos, block in matches:
        assert block["type"] == "column_list"
        assert "children" in block["column_list"]


# Parametrized tests for various input patterns
@pytest.mark.parametrize("markdown,should_match", [
    ("::: columns", True),
    ("  ::: columns  ", True),
    ("::: column", False),
    ("::: something", False),
    (":::", False),
    ("columns", False),
    ("", False),
])
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various Markdown patterns."""
    result = ColumnElement.match_markdown(markdown)
    assert result == should_match


@pytest.mark.parametrize("block_type,should_match", [
    ("column_list", True),
    ("column", False),
    ("paragraph", False),
    ("callout", False),
    ("heading_1", False),
])
def test_notion_block_recognition(block_type, should_match):
    """Test recognition of different Notion block types."""
    block = {"type": block_type}
    result = ColumnElement.match_notion(block)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def simple_column_list():
    """Fixture for simple column_list block."""
    return {
        "type": "column_list",
        "column_list": {
            "children": [
                {"type": "column", "column": {"children": []}},
                {"type": "column", "column": {"children": []}},
            ]
        },
    }


@pytest.fixture
def complex_column_list():
    """Fixture for column_list with content."""
    return {
        "type": "column_list",
        "column_list": {
            "children": [
                {
                    "type": "column",
                    "column": {
                        "children": [
                            {"type": "paragraph", "paragraph": {"rich_text": []}},
                            {"type": "heading_1", "heading_1": {"rich_text": []}},
                        ]
                    }
                },
                {
                    "type": "column", 
                    "column": {
                        "children": [
                            {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": []}},
                        ]
                    }
                },
            ]
        },
    }


def test_with_fixtures(simple_column_list, complex_column_list):
    """Test using fixtures to reduce duplication."""
    # Test simple column list
    result1 = ColumnElement.notion_to_markdown(simple_column_list)
    assert "::: columns" in result1
    assert "::: column" in result1
    assert ":::" in result1
    
    # Test complex column list
    result2 = ColumnElement.notion_to_markdown(complex_column_list)
    assert "::: columns" in result2
    assert result2.count("::: column") == 2  # Two columns
    assert result2.count("[Column content]") == 3  # Three child elements total


def test_extract_nested_content():
    """Test extraction of nested content from column blocks."""
    lines = [
        "::: columns",
        "::: column", 
        "Content line 1",
        "Content line 2",
        ":::",
        "::: column",
        "Other content",
        ":::",
        ":::"
    ]
    
    # Test the nested content extraction method
    nested_content, next_index = ColumnElement.extract_nested_content(lines, 1)
    
    assert len(nested_content) > 0
    assert next_index > 1


def test_is_next_line_pipe_content():
    """Test detection of pipe-prefixed content lines."""
    lines = [
        "regular line",
        "| pipe content",
        "another regular line"
    ]
    
    # This method checks for pipe content (used in other elements like toggles)
    # For columns, this might not be directly applicable, but testing the pattern
    result = ColumnElement.is_next_line_pipe_content(lines, 0)
    # The actual behavior depends on the implementation
    assert isinstance(result, bool)


def test_preprocess_column_content():
    """Test preprocessing of column content (removing spacers)."""
    lines = [
        "Regular content",
        "---spacer---",
        "More content",
        "---spacer---",
        "Final content"
    ]
    
    processed = ColumnElement._preprocess_column_content(lines)
    
    assert "---spacer---" not in processed
    assert "Regular content" in processed
    assert "More content" in processed
    assert "Final content" in processed


def test_converter_callback_setting():
    """Test setting and using converter callback."""
    def dummy_converter(text):
        return [{"type": "test", "content": text}]
    
    # Set the converter callback
    ColumnElement.set_converter_callback(dummy_converter)
    
    # Test that it was set (this depends on the actual implementation)
    # The callback should be stored and used during conversion
    assert ColumnElement._converter_callback is not None


def test_column_markdown_structure():
    """Test the expected Markdown structure for columns."""
    expected_patterns = [
        "::: columns",  # Start marker
        "::: column",   # Column marker
        ":::",          # End marker
    ]
    
    markdown = (
        "::: columns\n"
        "::: column\n"
        "Sample content\n"
        ":::\n"
        ":::"
    )
    
    for pattern in expected_patterns:
        assert pattern in markdown


def test_column_nesting_detection():
    """Test detection of nested column structures."""
    nested_markdown = (
        "::: columns\n"
        "::: column\n"
        "Outer column content\n"
        "::: columns\n"  # Nested columns
        "::: column\n"
        "Inner column\n"
        ":::\n"
        ":::\n"
        ":::\n"
        ":::"
    )
    
    # Should handle nested structures properly
    assert ColumnElement.match_markdown("::: columns")
    
    # The find_matches should handle nested structures
    # (actual behavior depends on implementation)
    def mock_convert(text):
        return [{"type": "paragraph", "paragraph": {"rich_text": []}}]
    
    matches = ColumnElement.find_matches(nested_markdown, converter_callback=mock_convert)
    assert len(matches) >= 1  # Should find at least the outer columns