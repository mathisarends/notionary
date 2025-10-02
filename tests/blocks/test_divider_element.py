import pytest

from notionary.blocks.divider.divider_element import DividerElement
from notionary.blocks.divider.models import CreateDividerBlock, DividerBlock
from notionary.blocks.models import Block


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
async def test_match_markdown_valid():
    """Test recognition of valid divider syntax."""
    assert await DividerElement.markdown_to_notion("---") is not None
    assert await DividerElement.markdown_to_notion("----")  # More dashes
    assert await DividerElement.markdown_to_notion("-----") is not None
    assert await DividerElement.markdown_to_notion("  ---  ")  # With spaces


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not await DividerElement.markdown_to_notion("--")  # Too few dashes
    assert not await DividerElement.markdown_to_notion("text ---")  # Not alone
    assert await DividerElement.markdown_to_notion("--- text") is None
    assert await DividerElement.markdown_to_notion("This is just text.") is None


def test_match_notion():
    """Test recognition of Notion divider blocks."""
    divider_block = create_block_with_required_fields(
        type="divider",
        divider=DividerBlock(),
    )
    assert DividerElement.match_notion(divider_block)

    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert not DividerElement.match_notion(paragraph_block)

    # Test divider block without divider property
    invalid_divider = create_block_with_required_fields(type="divider")
    assert not DividerElement.match_notion(invalid_divider)


@pytest.mark.asyncio
async def test_markdown_to_notion():
    """Test conversion of divider to Notion blocks."""
    result = await DividerElement.markdown_to_notion("---")

    # Should return just the divider block
    assert isinstance(result, CreateDividerBlock)
    assert result.type == "divider"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = await DividerElement.markdown_to_notion("--")  # Too few dashes
    assert result is None

    result = await DividerElement.markdown_to_notion("text ---")
    assert result is None


@pytest.mark.asyncio
async def test_notion_to_markdown():
    """Test conversion of Notion divider to markdown."""
    block = create_block_with_required_fields(
        type="divider",
        divider=DividerBlock(),
    )

    result = await DividerElement.notion_to_markdown(block)
    assert result == "---"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    paragraph_block = create_block_with_required_fields(type="paragraph")
    result = await DividerElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Test divider block without divider property
    invalid_divider = create_block_with_required_fields(type="divider")
    result = await DividerElement.notion_to_markdown(invalid_divider)
    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("---", True),
        ("----", True),
        ("-----", True),
        ("  ---  ", True),
        ("--", False),
        ("text ---", False),
        ("--- text", False),
        ("", False),
    ],
)
async def test_markdown_patterns(markdown, should_match):
    """Test recognition of various divider patterns."""
    result = await DividerElement.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None
