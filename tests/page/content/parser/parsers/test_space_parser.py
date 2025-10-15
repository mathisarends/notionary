from textwrap import dedent

import pytest

from notionary.blocks.enums import BlockType
from notionary.page.content.factory import PageContentServiceFactory
from notionary.page.content.parser.service import MarkdownToNotionConverter


@pytest.fixture
def parser() -> MarkdownToNotionConverter:
    factory = PageContentServiceFactory()
    return factory._create_markdown_to_notion_converter()


@pytest.mark.asyncio
async def test_explicit_space_marker_creates_space_block(parser: MarkdownToNotionConverter):
    markdown = dedent("""
        First paragraph

        [space]

        Second paragraph
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 3
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[1].type == BlockType.PARAGRAPH
    assert blocks[1].paragraph.rich_text == []
    assert blocks[2].type == BlockType.PARAGRAPH


@pytest.mark.asyncio
async def test_single_empty_line_does_not_create_space_block(parser: MarkdownToNotionConverter):
    markdown = dedent("""
        First paragraph

        Second paragraph
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 2
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[1].type == BlockType.PARAGRAPH


@pytest.mark.asyncio
async def test_two_consecutive_empty_lines_create_space_block(parser: MarkdownToNotionConverter):
    markdown = dedent("""
        First paragraph


        Second paragraph
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 3
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[0].paragraph.rich_text[0].plain_text == "First paragraph"

    assert blocks[1].type == BlockType.PARAGRAPH
    assert blocks[1].paragraph.rich_text == []

    assert blocks[2].type == BlockType.PARAGRAPH
    assert blocks[2].paragraph.rich_text[0].plain_text == "Second paragraph"


@pytest.mark.asyncio
async def test_three_consecutive_empty_lines_create_two_space_blocks(parser: MarkdownToNotionConverter):
    markdown = dedent("""
        First paragraph



        Second paragraph
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 4
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[0].paragraph.rich_text[0].plain_text == "First paragraph"

    assert blocks[1].type == BlockType.PARAGRAPH
    assert blocks[1].paragraph.rich_text == []

    assert blocks[2].type == BlockType.PARAGRAPH
    assert blocks[2].paragraph.rich_text == []

    assert blocks[3].type == BlockType.PARAGRAPH
    assert blocks[3].paragraph.rich_text[0].plain_text == "Second paragraph"


@pytest.mark.asyncio
async def test_multiple_space_blocks_with_mixed_syntax(parser: MarkdownToNotionConverter):
    markdown = dedent("""
        First paragraph

        [space]

        Middle paragraph


        Last paragraph
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 5
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[0].paragraph.rich_text[0].plain_text == "First paragraph"

    assert blocks[1].type == BlockType.PARAGRAPH
    assert blocks[1].paragraph.rich_text == []

    assert blocks[2].type == BlockType.PARAGRAPH
    assert blocks[2].paragraph.rich_text[0].plain_text == "Middle paragraph"

    assert blocks[3].type == BlockType.PARAGRAPH
    assert blocks[3].paragraph.rich_text == []

    assert blocks[4].type == BlockType.PARAGRAPH
    assert blocks[4].paragraph.rich_text[0].plain_text == "Last paragraph"


@pytest.mark.asyncio
async def test_empty_lines_at_start_create_space_block(parser: MarkdownToNotionConverter):
    markdown = dedent("""


        First paragraph
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 3
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[0].paragraph.rich_text == []
    assert blocks[1].type == BlockType.PARAGRAPH
    assert blocks[1].paragraph.rich_text == []
    assert blocks[2].type == BlockType.PARAGRAPH
    assert blocks[2].paragraph.rich_text[0].plain_text == "First paragraph"


@pytest.mark.asyncio
async def test_empty_lines_at_end_create_space_blocks(parser: MarkdownToNotionConverter):
    markdown = dedent("""
        First paragraph


    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 3
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[0].paragraph.rich_text[0].plain_text == "First paragraph"

    assert blocks[1].type == BlockType.PARAGRAPH
    assert blocks[1].paragraph.rich_text == []

    assert blocks[2].type == BlockType.PARAGRAPH
    assert blocks[2].paragraph.rich_text == []


@pytest.mark.asyncio
async def test_space_blocks_with_toggle_syntax(parser: MarkdownToNotionConverter):
    markdown = dedent("""
        +++ Toggle Title
            Content inside toggle
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 1
    assert blocks[0].type == BlockType.TOGGLE
