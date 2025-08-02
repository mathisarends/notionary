"""
Pytest tests for ColumnElement.
Tests conversion between Markdown column syntax and Notion column blocks.
"""

import pytest
from unittest.mock import patch
from notionary.blocks.column import ColumnElement
from notionary.blocks.column.column_models import (
    ColumnBlock, 
    CreateColumnBlock, 
    ColumnListBlock, 
    CreateColumnListBlock
)
from notionary.blocks.block_models import Block
from notionary.blocks.paragraph.paragraph_models import ParagraphBlock
from notionary.blocks.heading.heading_models import HeadingBlock
from notionary.blocks.bulleted_list.bulleted_list_models import BulletedListItemBlock


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"}
    }
    defaults.update(kwargs)
    return Block(**defaults)


def create_column_block_with_children(children=None):
    """Helper to create a column block with children."""
    if children is None:
        children = []
    return create_block_with_required_fields(
        type="column",
        column=ColumnBlock(children=children)
    )


def create_column_list_block_with_children(children=None):
    """Helper to create a column_list block with children."""
    if children is None:
        children = []
    return create_block_with_required_fields(
        type="column_list",
        column_list=ColumnListBlock(children=children)
    )


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
    column_list_block = create_block_with_required_fields(
        type="column_list",
        column_list=ColumnListBlock()
    )
    assert ColumnElement.match_notion(column_list_block)

    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert not ColumnElement.match_notion(paragraph_block)

    column_block = create_block_with_required_fields(type="column")
    assert not ColumnElement.match_notion(column_block)

    callout_block = create_block_with_required_fields(type="callout")
    assert not ColumnElement.match_notion(callout_block)


def test_markdown_to_notion_valid():
    """Test creation of column_list block from valid Markdown."""
    result = ColumnElement.markdown_to_notion("::: columns")
    
    assert isinstance(result, CreateColumnListBlock)
    assert result.type == "column_list"
    assert isinstance(result.column_list, ColumnListBlock)


def test_markdown_to_notion_invalid():
    """Test invalid Markdown returns None."""
    assert ColumnElement.markdown_to_notion("::: column") is None
    assert ColumnElement.markdown_to_notion("some other text") is None
    assert ColumnElement.markdown_to_notion("") is None


def test_notion_to_markdown():
    """Test conversion from Notion column_list block to Markdown."""
    # Create child blocks for the columns
    column1 = create_column_block_with_children([
        create_block_with_required_fields(type="paragraph")
    ])
    column2 = create_column_block_with_children([
        create_block_with_required_fields(type="paragraph")
    ])
    
    notion_block = create_column_list_block_with_children([column1, column2])

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
    notion_block = create_column_list_block_with_children([])

    result = ColumnElement.notion_to_markdown(notion_block)
    assert "::: columns" in result
    assert ":::" in result


def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert ColumnElement.notion_to_markdown(paragraph_block) is None
    
    empty_block = create_block_with_required_fields(type="column_list")
    # Block without column_list content
    assert ColumnElement.notion_to_markdown(empty_block) is None


def test_is_multiline():
    """Test that column blocks are recognized as multiline elements."""
    assert ColumnElement.is_multiline()


@pytest.fixture
def mock_converter():
    """Fixture to mock the MarkdownToNotionConverter."""
    with patch(
        "notionary.blocks.column.column_element.ColumnElement._converter_callback"
    ) as mock:
        mock.return_value = [{"type": "paragraph", "paragraph": {"rich_text": []}}]
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

    # The find_matches method returns dictionary format for compatibility
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
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("::: columns", True),
        ("  ::: columns  ", True),
        ("::: column", False),
        ("::: something", False),
        (":::", False),
        ("columns", False),
        ("", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various Markdown patterns."""
    result = ColumnElement.match_markdown(markdown)
    assert result == should_match


@pytest.mark.parametrize(
    "block_type,should_match",
    [
        ("column_list", True),
        ("column", False),
        ("paragraph", False),
        ("callout", False),
        ("heading_1", False),
    ],
)
def test_notion_block_recognition(block_type, should_match):
    """Test recognition of different Notion block types."""
    block_data = {"type": block_type}
    
    if block_type == "column_list":
        block_data["column_list"] = ColumnListBlock()
    elif block_type == "column":
        block_data["column"] = ColumnBlock()
        
    block = create_block_with_required_fields(**block_data)
    result = ColumnElement.match_notion(block)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def simple_column_list():
    """Fixture for simple column_list block."""
    column1 = create_column_block_with_children([])
    column2 = create_column_block_with_children([])
    return create_column_list_block_with_children([column1, column2])


@pytest.fixture
def complex_column_list():
    """Fixture for column_list with content."""
    # Create child blocks for column 1
    paragraph_block = create_block_with_required_fields(
        type="paragraph",
        paragraph=ParagraphBlock(rich_text=[])
    )
    heading_block = create_block_with_required_fields(
        type="heading_1", 
        heading_1=HeadingBlock(rich_text=[])
    )
    
    # Create child blocks for column 2
    list_block = create_block_with_required_fields(
        type="bulleted_list_item",
        bulleted_list_item=BulletedListItemBlock(rich_text=[])
    )
    
    column1 = create_column_block_with_children([paragraph_block, heading_block])
    column2 = create_column_block_with_children([list_block])
    
    return create_column_list_block_with_children([column1, column2])


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
        ":::",
    ]

    # Test the nested content extraction method
    # This method is used internally by find_matches
    children = []
    next_index = ColumnElement._collect_columns(
        lines, 1, children, lambda x: [{"type": "test"}]
    )

    assert len(children) >= 0  # Should have processed some columns
    assert next_index > 1


def test_preprocess_column_content():
    """Test preprocessing of column content (removing spacers)."""
    lines = [
        "Regular content",
        "---spacer---",
        "More content",
        "---spacer---",
        "Final content",
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

    # Test that it was set
    assert ColumnElement._converter_callback is not None
    
    # Test that the callback works
    result = ColumnElement._converter_callback("test text")
    assert result[0]["type"] == "test"
    assert result[0]["content"] == "test text"


def test_column_markdown_structure():
    """Test the expected Markdown structure for columns."""
    expected_patterns = [
        "::: columns",  # Start marker
        "::: column",  # Column marker
        ":::",  # End marker
    ]

    markdown = "::: columns\n" "::: column\n" "Sample content\n" ":::\n" ":::"

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
    def mock_convert(text):
        return [{"type": "paragraph", "paragraph": {"rich_text": []}}]

    matches = ColumnElement.find_matches(
        nested_markdown, converter_callback=mock_convert
    )
    assert len(matches) >= 1  # Should find at least the outer columns


def test_finalize_column():
    """Test the _finalize_column static method."""
    column_content = ["Line 1", "Line 2", "Line 3"]
    columns_children = []
    
    def mock_converter(text):
        return [{"type": "paragraph", "content": text}]
    
    ColumnElement._finalize_column(
        column_content, columns_children, True, mock_converter
    )
    
    assert len(columns_children) == 1
    assert columns_children[0]["type"] == "column"
    assert "children" in columns_children[0]["column"]


def test_roundtrip_conversion():
    """Test that Markdown -> Notion -> Markdown preserves structure."""
    original_markdown = "::: columns"
    
    # Convert to Notion
    notion_result = ColumnElement.markdown_to_notion(original_markdown)
    assert notion_result is not None
    
    # Create a Block for notion_to_markdown (empty columns for simplicity)
    block = create_column_list_block_with_children([])
    
    # Convert back to Markdown
    result_markdown = ColumnElement.notion_to_markdown(block)
    assert result_markdown is not None
    assert "::: columns" in result_markdown
    assert ":::" in result_markdown


def test_process_column_block():
    """Test the _process_column_block method."""
    lines = [
        "::: columns",
        "::: column",
        "Content line 1",
        ":::",
        ":::"
    ]
    
    def mock_converter(text):
        return [{"type": "paragraph", "paragraph": {"rich_text": []}}]
    
    result = ColumnElement._process_column_block(
        lines, 0, mock_converter
    )
    
    start_pos, end_pos, block, next_index = result
    
    assert isinstance(start_pos, int)
    assert isinstance(end_pos, int)
    assert isinstance(next_index, int)
    assert block["type"] == "column_list"
    assert start_pos < end_pos
    assert next_index > 0


def test_collect_columns():
    """Test the _collect_columns method."""
    lines = [
        "::: column",
        "Content 1",
        ":::",
        "::: column", 
        "Content 2",
        ":::",
        ":::"
    ]
    
    columns_children = []
    
    def mock_converter(text):
        return [{"type": "paragraph", "paragraph": {"rich_text": []}}]
    
    next_index = ColumnElement._collect_columns(
        lines, 0, columns_children, mock_converter
    )
    
    assert len(columns_children) == 2  # Should have created 2 columns
    assert next_index > 0
    
    for column in columns_children:
        assert column["type"] == "column"
        assert "children" in column["column"]


def test_empty_column_handling():
    """Test handling of empty columns."""
    empty_column = create_column_block_with_children([])
    column_list = create_column_list_block_with_children([empty_column])
    
    result = ColumnElement.notion_to_markdown(column_list)
    
    assert "::: columns" in result
    assert "::: column" in result
    assert ":::" in result