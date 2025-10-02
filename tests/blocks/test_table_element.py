from unittest.mock import Mock

import pytest

from notionary.blocks.rich_text.models import (
    RichText,
    TextAnnotations,
    TextContent,
)
from notionary.blocks.table.table_element import TableElement
from notionary.blocks.types import BlockType


def create_rich_text(content: str) -> RichText:
    """Helper to create RichText."""
    return RichText(
        type="text",
        text=TextContent(content=content),
        annotations=TextAnnotations(),
        plain_text=content,
    )


@pytest.mark.asyncio
async def test_notion_to_markdown_with_data():
    """Test conversion with actual table data."""
    # Create real RichText instances instead of dictionaries
    mock_cell_1 = [create_rich_text("John")]
    mock_cell_2 = [create_rich_text("25")]

    # Create mock table row with proper structure
    mock_row = Mock()
    mock_row.type = "table_row"  # String ist hier OK, da es child-type ist
    mock_row.table_row = Mock()
    mock_row.table_row.cells = [mock_cell_1, mock_cell_2]

    # Create mock table block with BlockType enum
    mock_block = Mock()
    mock_block.type = BlockType.TABLE  # BlockType enum statt String
    mock_block.table = Mock()
    mock_block.table.table_width = 2
    mock_block.table.has_column_header = True
    mock_block.table.has_row_header = False
    mock_block.children = [mock_row]

    result = await TableElement.notion_to_markdown(mock_block)

    assert result is not None
    lines = result.split("\n")
    assert len(lines) >= 2  # At least header + separator

    # Check that data is included
    assert "John" in result
    assert "25" in result
    assert "|" in result  # Table format


def test_match_notion():
    """Test Notion block matching."""
    # Valid table block
    block = Mock()
    block.type = BlockType.TABLE  # BlockType enum
    block.table = Mock()
    assert TableElement.match_notion(block)

    # Invalid - wrong type
    block.type = BlockType.PARAGRAPH
    assert not TableElement.match_notion(block)

    # Invalid - no table content
    block.type = BlockType.TABLE
    block.table = None
    assert not TableElement.match_notion(block)
