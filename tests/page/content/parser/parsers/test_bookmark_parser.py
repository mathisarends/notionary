import pytest

from notionary.blocks.schemas import CreateBookmarkBlock
from notionary.page.content.parser.context import BlockParsingContext
from notionary.page.content.parser.parsers.bookmark import BookmarkParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def bookmark_parser(syntax_registry: SyntaxRegistry) -> BookmarkParser:
    return BookmarkParser(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_valid_bookmark_syntax_should_create_bookmark_block(
    bookmark_parser: BookmarkParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[bookmark](https://example.com)"

    await bookmark_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateBookmarkBlock)


def test_bookmark_with_whitespace_url_should_not_be_handled(
    bookmark_parser: BookmarkParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[bookmark](   )"

    can_handle = bookmark_parser._can_handle(context)

    assert can_handle is False
