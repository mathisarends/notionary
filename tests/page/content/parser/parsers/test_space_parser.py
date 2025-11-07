from textwrap import dedent
from unittest.mock import AsyncMock

import pytest

from notionary.blocks.enums import BlockType
from notionary.file_upload.service import NotionFileUpload
from notionary.page.content.parser.factory import create_markdown_to_notion_converter
from notionary.page.content.parser.parsers.factory import create_line_parser
from notionary.page.content.parser.service import MarkdownToNotionConverter
from notionary.rich_text.markdown_to_rich_text.factory import (
    create_markdown_to_rich_text_converter,
)
from notionary.rich_text.markdown_to_rich_text.handlers import (
    create_pattern_matcher,
)
from notionary.shared.name_id_resolver import (
    DatabaseNameIdResolver,
    DataSourceNameIdResolver,
    PageNameIdResolver,
    PersonNameIdResolver,
)


@pytest.fixture
def mock_page_resolver() -> AsyncMock:
    resolver: PageNameIdResolver = AsyncMock(spec=PageNameIdResolver)
    resolver.resolve_name_to_id.return_value = "page-123"
    resolver.resolve_id_to_name.return_value = "Test Page"
    return resolver


@pytest.fixture
def mock_database_resolver() -> AsyncMock:
    resolver: DatabaseNameIdResolver = AsyncMock(spec=DatabaseNameIdResolver)
    resolver.resolve_name_to_id.return_value = "db-456"
    resolver.resolve_id_to_name.return_value = "Tasks DB"
    return resolver


@pytest.fixture
def mock_data_source_resolver() -> AsyncMock:
    resolver: DataSourceNameIdResolver = AsyncMock(spec=DataSourceNameIdResolver)
    resolver.resolve_name_to_id.return_value = "ds-789"
    resolver.resolve_id_to_name.return_value = "Test DataSource"
    return resolver


@pytest.fixture
def mock_person_resolver() -> AsyncMock:
    resolver: PersonNameIdResolver = AsyncMock(spec=PersonNameIdResolver)
    resolver.resolve_name_to_id.return_value = "user-789"
    resolver.resolve_id_to_name.return_value = "John Doe"
    return resolver


@pytest.fixture
def parser(
    mock_page_resolver,
    mock_database_resolver,
    mock_data_source_resolver,
    mock_person_resolver,
) -> MarkdownToNotionConverter:
    mock_file_upload = AsyncMock(spec=NotionFileUpload)

    pattern_matcher = create_pattern_matcher(
        page_resolver=mock_page_resolver,
        database_resolver=mock_database_resolver,
        data_source_resolver=mock_data_source_resolver,
        person_resolver=mock_person_resolver,
    )

    rich_text_converter = create_markdown_to_rich_text_converter(
        pattern_matcher=pattern_matcher
    )

    line_parser = create_line_parser(
        file_upload_service=mock_file_upload,
        rich_text_converter=rich_text_converter,
    )

    return create_markdown_to_notion_converter(line_parser=line_parser)


@pytest.mark.asyncio
async def test_explicit_space_marker_creates_space_block(
    parser: MarkdownToNotionConverter,
):
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
async def test_single_empty_line_does_not_create_space_block(
    parser: MarkdownToNotionConverter,
):
    markdown = dedent("""
        First paragraph

        Second paragraph
    """)

    blocks = await parser.convert(markdown)

    assert len(blocks) == 2
    assert blocks[0].type == BlockType.PARAGRAPH
    assert blocks[1].type == BlockType.PARAGRAPH


@pytest.mark.asyncio
async def test_two_consecutive_empty_lines_create_space_block(
    parser: MarkdownToNotionConverter,
):
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
async def test_three_consecutive_empty_lines_create_two_space_blocks(
    parser: MarkdownToNotionConverter,
):
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
async def test_multiple_space_blocks_with_mixed_syntax(
    parser: MarkdownToNotionConverter,
):
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
async def test_empty_lines_at_start_create_space_block(
    parser: MarkdownToNotionConverter,
):
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
async def test_empty_lines_at_end_create_space_blocks(
    parser: MarkdownToNotionConverter,
):
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
