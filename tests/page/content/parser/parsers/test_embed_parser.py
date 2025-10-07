from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateEmbedBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.embed import EmbedParser


@pytest.fixture
def embed_parser() -> EmbedParser:
    return EmbedParser()


@pytest.mark.asyncio
async def test_embed_should_create_embed_block(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[embed](https://example.com/content)"

    await embed_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateEmbedBlock)
    assert block.embed.url == "https://example.com/content"
    assert block.embed.caption == []


@pytest.mark.asyncio
async def test_embed_with_http_url_should_create_block(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[embed](http://example.com/content)"

    await embed_parser._process(context)

    block = context.result_blocks[0]
    assert block.embed.url == "http://example.com/content"


@pytest.mark.parametrize(
    "line",
    [
        "[embed](https://example.com/page)",
        "[embed](https://youtube.com/watch?v=abc123)",
        "[embed](https://www.notion.so/page)",
        "[embed](http://example.com/content)",
        "[embed](https://example.com/path/to/content?param=value)",
    ],
)
def test_embed_with_valid_url_should_handle(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = embed_parser._can_handle(context)

    assert can_handle is True


def test_embed_inside_parent_context_should_not_handle(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[embed](https://example.com/content)"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = embed_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "[embed]",
        "[embed]()",
        "[embed](example.com)",
        "[embed](ftp://example.com/file)",
        "[embed](//example.com/content)",
        "[EMBED](https://example.com/content)",
        "[ embed ](https://example.com/content)",
        "embed(https://example.com/content)",
        "[embed](https://example.com/content",
        "[embed]https://example.com/content)",
        "[embed](https://example.com with space)",
        "[image](https://example.com/photo.jpg)",
    ],
)
def test_embed_with_invalid_syntax_should_not_handle(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = embed_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_embed_with_query_parameters_should_create_block(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[embed](https://youtube.com/watch?v=abc123&t=30s)"

    await embed_parser._process(context)

    block = context.result_blocks[0]
    assert block.embed.url == "https://youtube.com/watch?v=abc123&t=30s"


@pytest.mark.asyncio
async def test_embed_with_text_before_and_after_should_create_block(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "Check out this: [embed](https://example.com/content) it's great!"

    await embed_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.embed.url == "https://example.com/content"


@pytest.mark.asyncio
async def test_embed_with_fragment_should_create_block(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[embed](https://example.com/page#section)"

    await embed_parser._process(context)

    block = context.result_blocks[0]
    assert block.embed.url == "https://example.com/page#section"


@pytest.mark.asyncio
async def test_embed_should_append_block_to_result_blocks(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[embed](https://example.com/content)"
    initial_length = len(context.result_blocks)

    await embed_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1


@pytest.mark.asyncio
async def test_embed_with_port_number_should_create_block(
    embed_parser: EmbedParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[embed](https://example.com:8080/content)"

    await embed_parser._process(context)

    block = context.result_blocks[0]
    assert block.embed.url == "https://example.com:8080/content"
