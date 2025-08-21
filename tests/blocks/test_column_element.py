"""
Pytest tests for ColumnElement.
Tests the essential functionality for column block handling.
"""

import pytest

from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.column.column_models import (ColumnBlock,
                                                   CreateColumnBlock)
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
    """Test recognition of valid column start syntax."""
    assert ColumnElement.markdown_to_notion("::: column") is not None
    assert ColumnElement.markdown_to_notion(":::column")  # No space
    assert ColumnElement.markdown_to_notion("::: column ")  # Trailing space


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert ColumnElement.markdown_to_notion("This is just text.") is None
    assert not ColumnElement.markdown_to_notion(":: column")  # Wrong marker
    assert not ColumnElement.markdown_to_notion("::: columns")  # Plural
    assert not ColumnElement.markdown_to_notion("text ::: column")  # Not at start


def test_match_notion():
    """Test recognition of Notion column blocks."""
    column_block = create_block_with_required_fields(
        type="column",
        column=ColumnBlock(width_ratio=None),
    )
    assert ColumnElement.match_notion(column_block)

    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert not ColumnElement.match_notion(paragraph_block)


def test_markdown_to_notion():
    """Test conversion of column start to Notion ColumnBlock."""
    result = ColumnElement.markdown_to_notion("::: column")

    assert isinstance(result, CreateColumnBlock)
    assert result.type == "column"
    assert result.column.width_ratio is None  # Default ratio


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = ColumnElement.markdown_to_notion("This is just text.")
    assert result is None

    result = ColumnElement.markdown_to_notion(":: column")  # Wrong syntax
    assert result is None


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("::: column", True),
        (":::column", True),
        ("::: column ", True),
        (":: column", False),
        ("::: columns", False),
        ("text ::: column", False),
        ("", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various column patterns."""
    result = ColumnElement.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None
