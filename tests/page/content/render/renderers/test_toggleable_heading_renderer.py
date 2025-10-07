from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Heading1Block, Heading2Block, Heading3Block, HeadingData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.toggleable_heading import ToggleableHeadingRenderer


def _create_heading_data(title: str, is_toggleable: bool = True) -> HeadingData:
    return HeadingData(
        rich_text=[RichText.from_plain_text(title)],
        is_toggleable=is_toggleable,
    )


def _create_toggleable_heading1_block(title: str) -> Heading1Block:
    mock_obj = Mock(spec=Heading1Block)
    block = cast(Heading1Block, mock_obj)
    block.type = BlockType.HEADING_1
    block.heading_1 = _create_heading_data(title, is_toggleable=True)
    return block


def _create_toggleable_heading2_block(title: str) -> Heading2Block:
    mock_obj = Mock(spec=Heading2Block)
    block = cast(Heading2Block, mock_obj)
    block.type = BlockType.HEADING_2
    block.heading_2 = _create_heading_data(title, is_toggleable=True)
    return block


def _create_toggleable_heading3_block(title: str) -> Heading3Block:
    mock_obj = Mock(spec=Heading3Block)
    block = cast(Heading3Block, mock_obj)
    block.type = BlockType.HEADING_3
    block.heading_3 = _create_heading_data(title, is_toggleable=True)
    return block


def _create_non_toggleable_heading1_block(title: str = "Not toggleable") -> Heading1Block:
    mock_obj = Mock(spec=Heading1Block)
    block = cast(Heading1Block, mock_obj)
    block.type = BlockType.HEADING_1
    block.heading_1 = _create_heading_data(title, is_toggleable=False)
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
    # The toggle delimiter is now in SyntaxRegistry, not as a constant on the renderer
    syntax = toggleable_heading_renderer._syntax_registry.get_toggleable_heading_syntax()
    assert syntax.start_delimiter == "+++ #"


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
