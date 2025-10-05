from unittest.mock import Mock

import pytest

from notionary.blocks.mappings.heading import HeadingMapper
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import BlockType, CreateHeadingData


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid heading formats."""
    assert await HeadingMapper.markdown_to_notion("# Heading 1") is not None
    assert await HeadingMapper.markdown_to_notion("## Heading 2") is not None
    assert await HeadingMapper.markdown_to_notion("### Heading 3") is not None
    assert await HeadingMapper.markdown_to_notion("#  Heading with spaces") is not None


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert await HeadingMapper.markdown_to_notion("#### Too deep") is None
    assert await HeadingMapper.markdown_to_notion("#No space") is None
    assert not await HeadingMapper.markdown_to_notion("# ")  # No content
    assert await HeadingMapper.markdown_to_notion("Regular text") is None
    assert await HeadingMapper.markdown_to_notion("") is None


def test_match_notion():
    """Test recognition of Notion heading blocks."""
    heading_types = [
        (1, BlockType.HEADING_1, "heading_1"),
        (2, BlockType.HEADING_2, "heading_2"),
        (3, BlockType.HEADING_3, "heading_3"),
    ]

    for _level, block_type, attr_name in heading_types:
        block = Mock()
        block.type = block_type  # BlockType enum statt String
        setattr(block, attr_name, Mock())  # Not None
        assert HeadingMapper.match_notion(block)

    # Invalid blocks
    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH  # BlockType enum statt String
    assert not HeadingMapper.match_notion(paragraph_block)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown,expected_level,expected_content",
    [
        ("# Title", 1, "Title"),
        ("## Subtitle", 2, "Subtitle"),
        ("### Section", 3, "Section"),
    ],
)
async def test_markdown_to_notion(markdown, expected_level, expected_content):
    """Test conversion from markdown to Notion."""
    result = await HeadingMapper.markdown_to_notion(markdown)

    assert result is not None
    assert result.type == f"heading_{expected_level}"

    # Check heading content
    heading = getattr(result, f"heading_{expected_level}")
    assert isinstance(heading, CreateHeadingData)
    assert heading.is_toggleable is False
    assert heading.color == "default"
    assert len(heading.rich_text) > 0
    assert heading.rich_text[0].plain_text == expected_content


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert await HeadingMapper.markdown_to_notion("#### Too deep") is None
    assert await HeadingMapper.markdown_to_notion("#No space") is None
    assert await HeadingMapper.markdown_to_notion("# ") is None
    assert await HeadingMapper.markdown_to_notion("text") is None


@pytest.mark.asyncio
async def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Create mock block
    block = Mock()
    block.type = BlockType.HEADING_2

    # Mock heading content with real RichText
    heading_content = Mock()
    rich_text = RichText.from_plain_text("Test Heading")
    heading_content.rich_text = [rich_text]

    block.heading_2 = heading_content

    result = await HeadingMapper.notion_to_markdown(block)
    assert result == "## Test Heading"


def test_pattern_matching():
    """Test the regex pattern directly."""
    # Valid patterns
    assert HeadingMapper.PATTERN.match("# Title")
    assert HeadingMapper.PATTERN.match("## Subtitle")
    assert HeadingMapper.PATTERN.match("### Section")

    # Invalid patterns
    assert not HeadingMapper.PATTERN.match("#### Too deep")
    assert not HeadingMapper.PATTERN.match("#NoSpace")
    assert not HeadingMapper.PATTERN.match("Regular text")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("# Heading 1", True),
        ("## Heading 2", True),
        ("### Heading 3", True),
        ("#### Heading 4", False),  # Too deep
        ("#NoSpace", False),  # No space
        ("# ", False),  # No content
        ("Regular text", False),
        ("", False),
    ],
)
async def test_markdown_patterns(markdown, should_match):
    """Test various markdown patterns."""
    result = await HeadingMapper.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None
