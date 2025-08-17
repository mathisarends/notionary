"""
Pytest tests for DividerElement.
Tests the essential functionality for divider block handling.
"""

import pytest
from notionary.blocks.divider.divider_element import DividerElement
from notionary.blocks.divider.divider_models import CreateDividerBlock, DividerBlock
from notionary.blocks.paragraph.paragraph_models import CreateParagraphBlock
from notionary.blocks.models import Block


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"},
    }
    defaults.update(kwargs)
    return Block(**defaults)


def test_match_markdown_valid():
    """Test recognition of valid divider syntax."""
    assert DividerElement.markdown_to_notion("---") is not None
    assert DividerElement.markdown_to_notion("----")  # More dashes
    assert DividerElement.markdown_to_notion("-----") is not None
    assert DividerElement.markdown_to_notion("  ---  ")  # With spaces


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not DividerElement.markdown_to_notion("--")  # Too few dashes
    assert not DividerElement.markdown_to_notion("text ---")  # Not alone
    assert DividerElement.markdown_to_notion("--- text") is None
    assert DividerElement.markdown_to_notion("This is just text.") is None


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


def test_markdown_to_notion():
    """Test conversion of divider to Notion blocks."""
    result = DividerElement.markdown_to_notion("---")

    assert len(result) == 2  # Empty paragraph + divider

    # First should be empty paragraph
    para_block = result[0]
    assert isinstance(para_block, CreateParagraphBlock)
    assert para_block.paragraph.rich_text == []

    # Second should be divider
    divider_block = result[1]
    assert isinstance(divider_block, CreateDividerBlock)
    assert divider_block.type == "divider"


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = DividerElement.markdown_to_notion("--")  # Too few dashes
    assert result is None

    result = DividerElement.markdown_to_notion("text ---")
    assert result is None


def test_notion_to_markdown():
    """Test conversion of Notion divider to markdown."""
    block = create_block_with_required_fields(
        type="divider",
        divider=DividerBlock(),
    )

    result = DividerElement.notion_to_markdown(block)
    assert result == "---"


def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    paragraph_block = create_block_with_required_fields(type="paragraph")
    result = DividerElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Test divider block without divider property
    invalid_divider = create_block_with_required_fields(type="divider")
    result = DividerElement.notion_to_markdown(invalid_divider)
    assert result is None


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
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various divider patterns."""
    result = DividerElement.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None
