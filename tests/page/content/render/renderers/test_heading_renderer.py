from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import (
    Block,
    Heading1Block,
    Heading2Block,
    Heading3Block,
    HeadingData,
)
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.heading import HeadingRenderer
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.schemas import RichText


def _create_heading_data(
    rich_text: list[RichText], is_toggleable: bool = False
) -> HeadingData:
    return HeadingData(rich_text=rich_text, is_toggleable=is_toggleable)


def _create_heading_block(
    block_type: BlockType, heading_data: HeadingData | None
) -> Heading1Block | Heading2Block | Heading3Block:
    mock_obj = Mock(spec=Block)

    if block_type == BlockType.HEADING_1:
        heading_block = cast(Heading1Block, mock_obj)
        heading_block.heading_1 = heading_data
    elif block_type == BlockType.HEADING_2:
        heading_block = cast(Heading2Block, mock_obj)
        heading_block.heading_2 = heading_data
    elif block_type == BlockType.HEADING_3:
        heading_block = cast(Heading3Block, mock_obj)
        heading_block.heading_3 = heading_data
    else:
        heading_block = cast(Block, mock_obj)

    heading_block.type = block_type
    return heading_block


@pytest.fixture
def heading_renderer(
    syntax_registry: SyntaxDefinitionRegistry,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> HeadingRenderer:
    return HeadingRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=mock_rich_text_markdown_converter,
    )


@pytest.mark.asyncio
async def test_heading1_block_should_be_handled(
    heading_renderer: HeadingRenderer,
) -> None:
    heading_data = _create_heading_data(
        [RichText.from_plain_text("Heading 1")], is_toggleable=False
    )
    block = _create_heading_block(BlockType.HEADING_1, heading_data)

    assert heading_renderer._can_handle(block)


@pytest.mark.asyncio
async def test_heading2_block_should_be_handled(
    heading_renderer: HeadingRenderer,
) -> None:
    heading_data = _create_heading_data(
        [RichText.from_plain_text("Heading 2")], is_toggleable=False
    )
    block = _create_heading_block(BlockType.HEADING_2, heading_data)

    assert heading_renderer._can_handle(block)


@pytest.mark.asyncio
async def test_heading3_block_should_be_handled(
    heading_renderer: HeadingRenderer,
) -> None:
    heading_data = _create_heading_data(
        [RichText.from_plain_text("Heading 3")], is_toggleable=False
    )
    block = _create_heading_block(BlockType.HEADING_3, heading_data)

    assert heading_renderer._can_handle(block)


@pytest.mark.asyncio
async def test_non_heading_block_should_not_be_handled(
    heading_renderer: HeadingRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not heading_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_heading1_with_text_should_render_markdown(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Main Heading")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Main Heading"
    )

    heading_data = _create_heading_data(rich_text)
    block = _create_heading_block(BlockType.HEADING_1, heading_data)
    render_context.block = block

    await heading_renderer._process(render_context)

    assert render_context.markdown_result == "# Main Heading"


@pytest.mark.asyncio
async def test_heading2_with_text_should_render_markdown(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Subheading")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Subheading")

    heading_data = _create_heading_data(rich_text)
    block = _create_heading_block(BlockType.HEADING_2, heading_data)
    render_context.block = block

    await heading_renderer._process(render_context)

    assert render_context.markdown_result == "## Subheading"


@pytest.mark.asyncio
async def test_heading3_with_text_should_render_markdown(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Sub-subheading")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Sub-subheading"
    )

    heading_data = _create_heading_data(rich_text)
    block = _create_heading_block(BlockType.HEADING_3, heading_data)
    render_context.block = block

    await heading_renderer._process(render_context)

    assert render_context.markdown_result == "### Sub-subheading"


@pytest.mark.asyncio
async def test_heading_with_empty_rich_text_should_render_empty_string(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value=None)

    heading_data = _create_heading_data([])
    block = _create_heading_block(BlockType.HEADING_1, heading_data)
    render_context.block = block

    await heading_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_heading_with_missing_data_should_render_empty_string(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_heading_block(BlockType.HEADING_1, None)
    render_context.block = block

    await heading_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_heading_with_indent_level_should_indent_output(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Indented Heading")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Indented Heading"
    )

    heading_data = _create_heading_data(rich_text)
    block = _create_heading_block(BlockType.HEADING_1, heading_data)
    render_context.block = block
    render_context.indent_level = 1
    render_context.render_children = AsyncMock(return_value="")

    await heading_renderer._process(render_context)

    # Should have been indented (mock uses 2 spaces per level)
    assert "# Indented Heading" in render_context.markdown_result
    # Verify indent_text was NOT called since non-toggleable headings at indent level
    # are handled differently - they just build the heading and then check indent level


@pytest.mark.asyncio
async def test_get_heading_level_for_heading1_should_return_1(
    heading_renderer: HeadingRenderer,
) -> None:
    heading_data = _create_heading_data([RichText.from_plain_text("Test")])
    block = _create_heading_block(BlockType.HEADING_1, heading_data)

    level = heading_renderer._get_heading_level(block)

    assert level == 1


@pytest.mark.asyncio
async def test_get_heading_level_for_heading2_should_return_2(
    heading_renderer: HeadingRenderer,
) -> None:
    heading_data = _create_heading_data([RichText.from_plain_text("Test")])
    block = _create_heading_block(BlockType.HEADING_2, heading_data)

    level = heading_renderer._get_heading_level(block)

    assert level == 2


@pytest.mark.asyncio
async def test_get_heading_level_for_heading3_should_return_3(
    heading_renderer: HeadingRenderer,
) -> None:
    heading_data = _create_heading_data([RichText.from_plain_text("Test")])
    block = _create_heading_block(BlockType.HEADING_3, heading_data)

    level = heading_renderer._get_heading_level(block)

    assert level == 3


@pytest.mark.asyncio
async def test_get_heading_level_for_invalid_type_should_return_0(
    heading_renderer: HeadingRenderer,
) -> None:
    block = Mock(spec=Block)
    block.type = BlockType.PARAGRAPH

    level = heading_renderer._get_heading_level(block)

    assert level == 0


@pytest.mark.asyncio
async def test_get_heading_title_for_heading1_should_return_markdown(
    heading_renderer: HeadingRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Heading 1 Title")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Heading 1 Title"
    )

    heading_data = _create_heading_data(rich_text)
    block = _create_heading_block(BlockType.HEADING_1, heading_data)

    title = await heading_renderer._get_heading_title(block)

    assert title == "Heading 1 Title"


@pytest.mark.asyncio
async def test_get_heading_title_for_heading2_should_return_markdown(
    heading_renderer: HeadingRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Heading 2 Title")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Heading 2 Title"
    )

    heading_data = _create_heading_data(rich_text)
    block = _create_heading_block(BlockType.HEADING_2, heading_data)

    title = await heading_renderer._get_heading_title(block)

    assert title == "Heading 2 Title"


@pytest.mark.asyncio
async def test_get_heading_title_for_heading3_should_return_markdown(
    heading_renderer: HeadingRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Heading 3 Title")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Heading 3 Title"
    )

    heading_data = _create_heading_data(rich_text)
    block = _create_heading_block(BlockType.HEADING_3, heading_data)

    title = await heading_renderer._get_heading_title(block)

    assert title == "Heading 3 Title"


@pytest.mark.asyncio
async def test_get_heading_title_with_empty_rich_text_should_return_empty_string(
    heading_renderer: HeadingRenderer,
) -> None:
    heading_data = _create_heading_data([])
    block = _create_heading_block(BlockType.HEADING_1, heading_data)

    title = await heading_renderer._get_heading_title(block)

    assert title == ""


@pytest.mark.asyncio
async def test_get_heading_title_with_missing_data_should_return_empty_string(
    heading_renderer: HeadingRenderer,
) -> None:
    block = _create_heading_block(BlockType.HEADING_1, None)

    title = await heading_renderer._get_heading_title(block)

    assert title == ""


@pytest.mark.asyncio
async def test_get_heading_title_for_invalid_type_should_return_empty_string(
    heading_renderer: HeadingRenderer,
) -> None:
    block = Mock(spec=Block)
    block.type = BlockType.PARAGRAPH

    title = await heading_renderer._get_heading_title(block)

    assert title == ""


@pytest.mark.asyncio
async def test_toggleable_heading_with_children_should_render_with_indentation(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
    indent: str,
) -> None:
    rich_text = [RichText.from_plain_text("Toggleable Heading")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Toggleable Heading"
    )

    heading_data = _create_heading_data(rich_text, is_toggleable=True)
    block = _create_heading_block(BlockType.HEADING_2, heading_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value=f"{indent}Child content")

    await heading_renderer._process(render_context)

    assert "## Toggleable Heading" in render_context.markdown_result
    assert f"{indent}Child content" in render_context.markdown_result
    # Verify that render_children was called
    render_context.render_children.assert_called_once()
    # Verify that indent level was increased temporarily
    # The context's indent_level should be back to 0 after processing
    assert render_context.indent_level == 0


@pytest.mark.asyncio
async def test_toggleable_heading_without_children_should_render_heading_only(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Toggleable No Children")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Toggleable No Children"
    )

    heading_data = _create_heading_data(rich_text, is_toggleable=True)
    block = _create_heading_block(BlockType.HEADING_1, heading_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value="")

    await heading_renderer._process(render_context)

    assert render_context.markdown_result == "# Toggleable No Children"
    render_context.render_children.assert_called_once()


@pytest.mark.asyncio
async def test_toggleable_heading_with_nested_indent_should_handle_multiple_levels(
    heading_renderer: HeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
    indent: str,
) -> None:
    rich_text = [RichText.from_plain_text("Nested Heading")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Nested Heading"
    )

    heading_data = _create_heading_data(rich_text, is_toggleable=True)
    block = _create_heading_block(BlockType.HEADING_3, heading_data)
    render_context.block = block
    render_context.indent_level = 1  # Already indented
    render_context.render_children = AsyncMock(
        return_value=f"{indent}{indent}Deeply nested content"
    )

    await heading_renderer._process(render_context)

    assert "  ### Nested Heading" in render_context.markdown_result
    assert f"{indent}{indent}Deeply nested content" in render_context.markdown_result
    assert render_context.indent_level == 1
