from unittest.mock import Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import CreateParagraphBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.paragraph import ParagraphParser


@pytest.fixture
def paragraph_parser(
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> ParagraphParser:
    return ParagraphParser(rich_text_converter=mock_rich_text_converter)


@pytest.mark.asyncio
async def test_simple_text_should_create_paragraph_block(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "This is a simple paragraph"

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateParagraphBlock)


@pytest.mark.asyncio
async def test_empty_line_should_not_be_handled(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = ""

    assert not paragraph_parser._can_handle(context)


@pytest.mark.asyncio
async def test_paragraph_with_inline_markdown_should_convert_rich_text(
    mock_rich_text_converter: MarkdownRichTextConverter, context: BlockParsingContext
) -> None:
    parser = ParagraphParser(rich_text_converter=mock_rich_text_converter)
    context.line = "Text with **bold** and *italic* formatting"

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with(
        "Text with **bold** and *italic* formatting"
    )


@pytest.mark.asyncio
async def test_paragraph_with_special_characters_should_work(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "Paragraph with special chars äöü and emoji 🎉"

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_paragraph_with_numbers_should_work(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "Paragraph with numbers 123 and symbols @#$"

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_paragraph_with_leading_whitespace_should_work(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "  Paragraph with leading spaces"

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_paragraph_with_trailing_whitespace_should_work(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "Paragraph with trailing spaces   "

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_paragraph_inside_parent_context_should_not_be_handled(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "Some paragraph text"
    context.is_inside_parent_context = Mock(return_value=True)

    assert not paragraph_parser._can_handle(context)


@pytest.mark.asyncio
async def test_paragraph_with_links_should_work(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "Check out [this link](https://example.com) for more info"

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_paragraph_with_code_inline_should_work(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "Use the `print()` function to output text"

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_paragraph_with_multiple_markdown_elements_should_work(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "**Bold**, *italic*, `code`, and [link](url) all together"

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_paragraph_with_only_whitespace_should_be_handled(
    paragraph_parser: ParagraphParser, context: BlockParsingContext
) -> None:
    context.line = "   "

    assert paragraph_parser._can_handle(context)
    await paragraph_parser._process(context)

    assert len(context.result_blocks) == 1
