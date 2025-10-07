from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, HeadingData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.toggleable_heading import ToggleableHeadingRenderer


def _create_toggleable_heading1_block(title: str) -> Block:
    block = Mock(spec=Block)
    block.type = BlockType.HEADING_1
    block.heading_1 = Mock(spec=HeadingData)
    block.heading_1.is_toggleable = True
    block.heading_1.rich_text = [RichText.from_plain_text(title)]
    block.heading_2 = None
    block.heading_3 = None
    return block


def _create_toggleable_heading2_block(title: str) -> Block:
    block = Mock(spec=Block)
    block.type = BlockType.HEADING_2
    block.heading_1 = None
    block.heading_2 = Mock(spec=HeadingData)
    block.heading_2.is_toggleable = True
    block.heading_2.rich_text = [RichText.from_plain_text(title)]
    block.heading_3 = None
    return block


def _create_toggleable_heading3_block(title: str) -> Block:
    block = Mock(spec=Block)
    block.type = BlockType.HEADING_3
    block.heading_1 = None
    block.heading_2 = None
    block.heading_3 = Mock(spec=HeadingData)
    block.heading_3.is_toggleable = True
    block.heading_3.rich_text = [RichText.from_plain_text(title)]
    return block


def _create_non_toggleable_heading1_block() -> Block:
    block = Mock(spec=Block)
    block.type = BlockType.HEADING_1
    block.heading_1 = Mock(spec=HeadingData)
    block.heading_1.is_toggleable = False
    block.heading_1.rich_text = [RichText.from_plain_text("Not toggleable")]
    return block


@pytest.fixture
def toggleable_heading_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> ToggleableHeadingRenderer:
    return ToggleableHeadingRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_toggleable_heading1_should_be_handled(toggleable_heading_renderer: ToggleableHeadingRenderer) -> None:
    block = _create_toggleable_heading1_block("Title")

    assert toggleable_heading_renderer._can_handle(block)


@pytest.mark.asyncio
async def test_toggleable_heading2_should_be_handled(toggleable_heading_renderer: ToggleableHeadingRenderer) -> None:
    block = _create_toggleable_heading2_block("Title")

    assert toggleable_heading_renderer._can_handle(block)


@pytest.mark.asyncio
async def test_toggleable_heading3_should_be_handled(toggleable_heading_renderer: ToggleableHeadingRenderer) -> None:
    block = _create_toggleable_heading3_block("Title")

    assert toggleable_heading_renderer._can_handle(block)


@pytest.mark.asyncio
async def test_non_toggleable_heading_should_not_be_handled(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
) -> None:
    block = _create_non_toggleable_heading1_block()

    assert not toggleable_heading_renderer._can_handle(block)


@pytest.mark.asyncio
async def test_toggleable_heading1_without_children_should_render_with_delimiters(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="My Heading")
    render_context.render_children = AsyncMock(return_value="")

    block = _create_toggleable_heading1_block("My Heading")
    render_context.block = block

    await toggleable_heading_renderer._process(render_context)

    assert render_context.markdown_result == "+++ # My Heading\n+++"


@pytest.mark.asyncio
async def test_toggleable_heading2_without_children_should_render_with_two_hashes(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Subheading")
    render_context.render_children = AsyncMock(return_value="")

    block = _create_toggleable_heading2_block("Subheading")
    render_context.block = block

    await toggleable_heading_renderer._process(render_context)

    assert render_context.markdown_result == "+++ ## Subheading\n+++"


@pytest.mark.asyncio
async def test_toggleable_heading3_without_children_should_render_with_three_hashes(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Sub-subheading")
    render_context.render_children = AsyncMock(return_value="")

    block = _create_toggleable_heading3_block("Sub-subheading")
    render_context.block = block

    await toggleable_heading_renderer._process(render_context)

    assert render_context.markdown_result == "+++ ### Sub-subheading\n+++"


@pytest.mark.asyncio
async def test_toggleable_heading_with_children_should_include_children_content(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Heading with content")
    render_context.render_children = AsyncMock(return_value="Child paragraph")

    block = _create_toggleable_heading1_block("Heading with content")
    render_context.block = block

    await toggleable_heading_renderer._process(render_context)

    assert render_context.markdown_result == "+++ # Heading with content\nChild paragraph\n+++"


@pytest.mark.asyncio
async def test_toggleable_heading_with_indentation_should_indent_delimiters(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Indented")
    render_context.render_children = AsyncMock(return_value="")
    render_context.indent_level = 1

    block = _create_toggleable_heading1_block("Indented")
    render_context.block = block

    await toggleable_heading_renderer._process(render_context)

    # Mock indent_text adds 2 spaces to both start and end delimiters
    assert render_context.markdown_result == "  +++ # Indented\n  +++"
    assert render_context.indent_text.call_count == 2


@pytest.mark.asyncio
async def test_toggleable_heading_delimiter_constant_should_be_correct(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
) -> None:
    assert toggleable_heading_renderer.TOGGLE_DELIMITER == "+++"


@pytest.mark.asyncio
async def test_get_heading_level_should_return_correct_level(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
) -> None:
    block1 = _create_toggleable_heading1_block("H1")
    block2 = _create_toggleable_heading2_block("H2")
    block3 = _create_toggleable_heading3_block("H3")

    assert toggleable_heading_renderer._get_heading_level(block1) == 1
    assert toggleable_heading_renderer._get_heading_level(block2) == 2
    assert toggleable_heading_renderer._get_heading_level(block3) == 3


@pytest.mark.asyncio
async def test_get_heading_title_should_convert_rich_text(
    toggleable_heading_renderer: ToggleableHeadingRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Converted Title")

    block = _create_toggleable_heading1_block("Converted Title")

    title = await toggleable_heading_renderer._get_heading_title(block)

    assert title == "Converted Title"
