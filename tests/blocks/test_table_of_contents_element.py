import pytest

from notionary.blocks.schemas import Block, BlockType
from notionary.blocks.table_of_contents.models import (
    CreateTableOfContentsBlock,
    TableOfContentsBlock,
)
from notionary.blocks.table_of_contents.table_of_contents_element import (
    TableOfContentsElement,
)
from notionary.blocks.types import BlockColor


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id", "type": "person", "person": {}},
        "last_edited_by": {"object": "user", "id": "user-id", "type": "person", "person": {}},
    }
    defaults.update(kwargs)
    return Block(**defaults)


@pytest.mark.asyncio
async def test_match_markdown_valid_default():
    """Test recognition of valid default TOC syntax."""
    assert await TableOfContentsElement.markdown_to_notion("[toc]") is not None
    assert await TableOfContentsElement.markdown_to_notion("[TOC]")  # Case insensitive
    assert await TableOfContentsElement.markdown_to_notion("  [toc]  ")  # With spaces


@pytest.mark.asyncio
async def test_match_markdown_valid_with_color():
    """Test recognition of valid TOC syntax with colors."""
    assert await TableOfContentsElement.markdown_to_notion("[toc](blue)")
    assert await TableOfContentsElement.markdown_to_notion("[toc](gray)")
    assert await TableOfContentsElement.markdown_to_notion("[toc](blue_background)")
    assert await TableOfContentsElement.markdown_to_notion("[toc](red_background)")
    assert await TableOfContentsElement.markdown_to_notion("[TOC](BLUE)")  # Case insensitive


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not await TableOfContentsElement.markdown_to_notion("toc")  # Missing brackets
    assert not await TableOfContentsElement.markdown_to_notion("[toc")  # Missing closing bracket
    assert not await TableOfContentsElement.markdown_to_notion("toc]")  # Missing opening bracket
    assert not await TableOfContentsElement.markdown_to_notion("[table_of_contents]")  # Wrong name
    assert not await TableOfContentsElement.markdown_to_notion("[toc]()")  # Empty parentheses
    assert not await TableOfContentsElement.markdown_to_notion("[breadcrumb]")  # Different element
    assert not await TableOfContentsElement.markdown_to_notion("")  # Empty string


def test_match_notion_valid():
    """Test recognition of valid table of contents blocks."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color=BlockColor.DEFAULT),
    )
    assert TableOfContentsElement.match_notion(block)


def test_match_notion_invalid():
    """Test rejection of invalid blocks."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH,
        table_of_contents=TableOfContentsBlock(color=BlockColor.DEFAULT),
    )
    assert not TableOfContentsElement.match_notion(paragraph_block)

    # Right type but no table_of_contents
    no_toc_block = create_block_with_required_fields(type=BlockType.TABLE_OF_CONTENTS, table_of_contents=None)
    assert not TableOfContentsElement.match_notion(no_toc_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_default():
    """Test conversion from default markdown to Notion blocks."""
    result = await TableOfContentsElement.markdown_to_notion("[toc]")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert isinstance(result.table_of_contents, TableOfContentsBlock)
    assert result.table_of_contents.color == "default"


@pytest.mark.asyncio
async def test_markdown_to_notion_with_color():
    """Test conversion from colored markdown to Notion blocks."""
    result = await TableOfContentsElement.markdown_to_notion("[toc](blue)")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert isinstance(result.table_of_contents, TableOfContentsBlock)
    assert result.table_of_contents.color == "blue"


@pytest.mark.asyncio
async def test_markdown_to_notion_with_background_color():
    """Test conversion with background colors."""
    result = await TableOfContentsElement.markdown_to_notion("[toc](blue_background)")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert isinstance(result.table_of_contents, TableOfContentsBlock)
    assert result.table_of_contents.color == "blue_background"


@pytest.mark.asyncio
async def test_markdown_to_notion_case_insensitive():
    """Test that color matching is case insensitive."""
    result = await TableOfContentsElement.markdown_to_notion("[TOC](BLUE)")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert result.table_of_contents.color == "blue"  # Should be lowercase


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await TableOfContentsElement.markdown_to_notion("toc") is None
    assert await TableOfContentsElement.markdown_to_notion("[table_of_contents]") is None
    assert await TableOfContentsElement.markdown_to_notion("[breadcrumb]") is None
    assert await TableOfContentsElement.markdown_to_notion("") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_default():
    """Test conversion from default Notion blocks to markdown."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color=BlockColor.DEFAULT),
    )

    result = await TableOfContentsElement.notion_to_markdown(block)
    assert result == "[toc]"


@pytest.mark.asyncio
async def test_notion_to_markdown_with_color():
    """Test conversion from colored Notion blocks to markdown."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color=BlockColor.BLUE),
    )

    result = await TableOfContentsElement.notion_to_markdown(block)
    assert result == "[toc](blue)"


@pytest.mark.asyncio
async def test_notion_to_markdown_with_background_color():
    """Test conversion with background colors."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color=BlockColor.BLUE_BACKGROUND),
    )

    result = await TableOfContentsElement.notion_to_markdown(block)
    assert result == "[toc](blue_background)"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH, table_of_contents=TableOfContentsBlock(color=BlockColor.BLUE)
    )
    assert await TableOfContentsElement.notion_to_markdown(paragraph_block) is None

    # Right type but no table_of_contents
    no_toc_block = create_block_with_required_fields(type=BlockType.TABLE_OF_CONTENTS, table_of_contents=None)
    assert await TableOfContentsElement.notion_to_markdown(no_toc_block) is None


@pytest.mark.asyncio
async def test_bidirectional_conversion():
    """Test that markdown -> notion -> markdown is consistent."""
    original_inputs = ["[toc]", "[toc](blue)", "[toc](gray_background)"]

    for original in original_inputs:
        notion_result = await TableOfContentsElement.markdown_to_notion(original)
        assert notion_result is not None

        block = create_block_with_required_fields(
            type=BlockType.TABLE_OF_CONTENTS,
            table_of_contents=notion_result.table_of_contents,
        )

        # Convert back to markdown
        markdown_result = await TableOfContentsElement.notion_to_markdown(block)
        assert markdown_result == original.lower()  # Should match (potentially lowercased)
