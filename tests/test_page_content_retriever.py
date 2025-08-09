"""
Functional tests for PageContentRetriever focusing on rich text and nested structures.
No pytest-asyncio dependency required.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from notionary.page.content.page_content_retriever import PageContentRetriever
from notionary.blocks.block_models import Block, BlockType


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"},
        "has_children": False,
        "children": None,
    }
    defaults.update(kwargs)
    return Block(**defaults)


def create_mock_registry_with_rich_text():
    """Create a realistic mock registry that handles rich text formatting."""
    registry = Mock()

    def mock_notion_to_markdown(block):
        """Mock that simulates real rich text conversion."""
        if block.type == BlockType.PARAGRAPH:
            return f"This is **bold** and *italic* text in paragraph {block.id}"
        elif block.type == BlockType.HEADING_1:
            return f"# **Heading** with rich text {block.id}"
        elif block.type == BlockType.COLUMN_LIST:
            return ""  # Column list itself produces no direct markdown
        elif block.type == BlockType.COLUMN:
            return ""  # Column wrapper produces no direct markdown
        elif block.type == BlockType.BULLETED_LIST_ITEM:
            return f"- List item with `code` and **bold** {block.id}"
        elif block.type == BlockType.CALLOUT:
            return f"> 💡 **Important:** This is a callout {block.id}"
        elif block.type == BlockType.TOGGLE:
            return f"+++ **Toggle** title {block.id}"
        else:
            return f"Block {block.id}"

    registry.notion_to_markdown = Mock(side_effect=mock_notion_to_markdown)
    return registry


def test_rich_text_formatting_preserved():
    """Test that rich text formatting is correctly preserved in output."""

    async def async_test():
        # Setup
        registry = create_mock_registry_with_rich_text()
        retriever = PageContentRetriever("test-page", registry)

        test_blocks = [
            create_block_with_required_fields(
                type=BlockType.HEADING_1, id="rich-heading"
            ),
            create_block_with_required_fields(
                type=BlockType.PARAGRAPH, id="rich-paragraph"
            ),
            create_block_with_required_fields(
                type=BlockType.BULLETED_LIST_ITEM, id="rich-list"
            ),
        ]

        # Mock the client
        with patch.object(retriever, "client") as mock_client:
            mock_client.get_blocks_by_page_id_recursively = AsyncMock(
                return_value=test_blocks
            )

            # Execute
            result = await retriever.get_page_content()

            # Verify rich text is preserved
            assert "# **Heading** with rich text rich-heading" in result
            assert (
                "This is **bold** and *italic* text in paragraph rich-paragraph"
                in result
            )
            assert "- List item with `code` and **bold** rich-list" in result

            # Verify structure (double newlines between root blocks)
            lines = result.split("\n")
            assert (
                len([line for line in lines if line == ""]) >= 2
            )  # At least 2 empty lines

    # Run the async test
    asyncio.run(async_test())


def test_column_layout_structure():
    """Test that column layouts are correctly processed with proper indentation."""

    async def async_test():
        # Setup realistic column layout
        registry = create_mock_registry_with_rich_text()
        retriever = PageContentRetriever("test-page", registry)

        # Create column content
        left_column_content = [
            create_block_with_required_fields(
                type=BlockType.HEADING_1, id="left-heading"
            ),
            create_block_with_required_fields(
                type=BlockType.PARAGRAPH, id="left-paragraph"
            ),
        ]

        right_column_content = [
            create_block_with_required_fields(
                type=BlockType.BULLETED_LIST_ITEM, id="right-item1"
            ),
            create_block_with_required_fields(
                type=BlockType.BULLETED_LIST_ITEM, id="right-item2"
            ),
        ]

        # Create column structure
        left_column = create_block_with_required_fields(
            type=BlockType.COLUMN,
            id="left-column",
            has_children=True,
            children=left_column_content,
        )

        right_column = create_block_with_required_fields(
            type=BlockType.COLUMN,
            id="right-column",
            has_children=True,
            children=right_column_content,
        )

        column_list = create_block_with_required_fields(
            type=BlockType.COLUMN_LIST,
            id="column-list",
            has_children=True,
            children=[left_column, right_column],
        )

        test_blocks = [
            create_block_with_required_fields(type=BlockType.PARAGRAPH, id="intro"),
            column_list,
            create_block_with_required_fields(
                type=BlockType.PARAGRAPH, id="conclusion"
            ),
        ]

        # Mock the client
        with patch.object(retriever, "client") as mock_client:
            mock_client.get_blocks_by_page_id_recursively = AsyncMock(
                return_value=test_blocks
            )

            # Execute
            result = await retriever.get_page_content()

            # Verify structure
            lines = result.split("\n")

            # Check that column content is indented (4 spaces for level 1, 8 for level 2)
            left_heading_line = next(line for line in lines if "left-heading" in line)
            assert left_heading_line.startswith("        ")  # 8 spaces (2 levels deep)

            right_item_line = next(line for line in lines if "right-item1" in line)
            assert right_item_line.startswith("        ")  # 8 spaces (2 levels deep)

            # Verify content order and structure
            assert "intro" in result
            assert "left-heading" in result
            assert "right-item1" in result
            assert "conclusion" in result

    # Run the async test
    asyncio.run(async_test())


def test_complex_nested_structure_with_toggles():
    """Test complex nested structure with toggles containing rich content."""

    async def async_test():
        registry = create_mock_registry_with_rich_text()
        retriever = PageContentRetriever("test-page", registry)

        # Create nested toggle content
        nested_content = [
            create_block_with_required_fields(
                type=BlockType.PARAGRAPH, id="nested-paragraph"
            ),
            create_block_with_required_fields(
                type=BlockType.CALLOUT, id="nested-callout"
            ),
        ]

        inner_toggle = create_block_with_required_fields(
            type=BlockType.TOGGLE,
            id="inner-toggle",
            has_children=True,
            children=nested_content,
        )

        outer_toggle_content = [
            create_block_with_required_fields(
                type=BlockType.PARAGRAPH, id="outer-paragraph"
            ),
            inner_toggle,
        ]

        outer_toggle = create_block_with_required_fields(
            type=BlockType.TOGGLE,
            id="outer-toggle",
            has_children=True,
            children=outer_toggle_content,
        )

        test_blocks = [
            create_block_with_required_fields(
                type=BlockType.HEADING_1, id="main-heading"
            ),
            outer_toggle,
        ]

        # Mock the client
        with patch.object(retriever, "client") as mock_client:
            mock_client.get_blocks_by_page_id_recursively = AsyncMock(
                return_value=test_blocks
            )

            # Execute
            result = await retriever.get_page_content()

            # Verify nested indentation levels
            lines = result.split("\n")

            # Level 0: Main heading (no indent)
            main_heading = next(line for line in lines if "main-heading" in line)
            assert not main_heading.startswith(" ")

            # Level 1: Outer toggle (4 spaces)
            outer_toggle_line = next(line for line in lines if "outer-toggle" in line)
            assert outer_toggle_line.startswith(
                "    "
            ) and not outer_toggle_line.startswith("        ")

            # Level 2: Content inside outer toggle (8 spaces)
            outer_paragraph = next(line for line in lines if "outer-paragraph" in line)
            assert outer_paragraph.startswith("        ")

            # Level 2: Inner toggle (8 spaces)
            inner_toggle_line = next(line for line in lines if "inner-toggle" in line)
            assert inner_toggle_line.startswith("        ")

            # Level 3: Content inside inner toggle (12 spaces)
            nested_paragraph = next(
                line for line in lines if "nested-paragraph" in line
            )
            assert nested_paragraph.startswith("            ")

            nested_callout = next(line for line in lines if "nested-callout" in line)
            assert nested_callout.startswith("            ")

    # Run the async test
    asyncio.run(async_test())


def test_indent_text_preserves_rich_formatting():
    """Test that indentation doesn't break rich text formatting."""
    registry = create_mock_registry_with_rich_text()
    retriever = PageContentRetriever("test-page", registry)

    # Test rich text with various markdown
    rich_text = "This has **bold**, *italic*, `code`, and [links](http://example.com)"

    result = retriever._indent_text(rich_text, 4)

    # Verify formatting is preserved
    assert "**bold**" in result
    assert "*italic*" in result
    assert "`code`" in result
    assert "[links](http://example.com)" in result
    assert result.startswith("    ")


def test_multiline_rich_text_indentation():
    """Test indentation of multiline rich text content."""
    registry = create_mock_registry_with_rich_text()
    retriever = PageContentRetriever("test-page", registry)

    # Multiline content with rich formatting
    content = """**First line** with bold
*Second line* with italic
`Third line` with code
Normal fourth line"""

    result = retriever._indent_text(content, 4)

    lines = result.split("\n")

    # All lines should be indented
    assert all(line.startswith("    ") for line in lines)

    # Formatting should be preserved
    assert "**First line**" in lines[0]
    assert "*Second line*" in lines[1]
    assert "`Third line`" in lines[2]


def test_empty_children_handling():
    """Test handling of blocks that have children flag but empty/null children."""

    async def async_test():
        registry = create_mock_registry_with_rich_text()
        retriever = PageContentRetriever("test-page", registry)

        test_blocks = [
            # Block with has_children=True but children=None
            create_block_with_required_fields(
                type=BlockType.TOGGLE,
                id="empty-toggle",
                has_children=True,
                children=None,
            ),
            # Block with has_children=True but children=[]
            create_block_with_required_fields(
                type=BlockType.TOGGLE,
                id="empty-list-toggle",
                has_children=True,
                children=[],
            ),
            # Normal block for comparison
            create_block_with_required_fields(
                type=BlockType.PARAGRAPH, id="normal-paragraph"
            ),
        ]

        with patch.object(retriever, "client") as mock_client:
            mock_client.get_blocks_by_page_id_recursively = AsyncMock(
                return_value=test_blocks
            )

            result = await retriever.get_page_content()

            # Should handle gracefully without errors
            assert "empty-toggle" in result
            assert "empty-list-toggle" in result
            assert "normal-paragraph" in result

            # No extra indentation or weird formatting
            lines = result.split("\n")
            toggle_lines = [
                line
                for line in lines
                if "empty-toggle" in line or "empty-list-toggle" in line
            ]

            # Both should be at root level (no indentation)
            for line in toggle_lines:
                assert not line.startswith("    ")

    # Run the async test
    asyncio.run(async_test())
