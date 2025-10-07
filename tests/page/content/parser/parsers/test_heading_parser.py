from unittest.mock import Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import (
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.heading import HeadingParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def heading_parser(
    mock_rich_text_converter: MarkdownRichTextConverter, syntax_registry: SyntaxRegistry
) -> HeadingParser:
    return HeadingParser(syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter)


@pytest.mark.asyncio
async def test_heading_level_1_should_create_heading1_block(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "# Heading Level 1"

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateHeading1Block)


@pytest.mark.asyncio
async def test_heading_level_2_should_create_heading2_block(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "## Heading Level 2"

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateHeading2Block)


@pytest.mark.asyncio
async def test_heading_level_3_should_create_heading3_block(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "### Heading Level 3"

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateHeading3Block)


@pytest.mark.asyncio
async def test_heading_level_4_should_not_be_handled(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "#### Heading Level 4"

    assert not heading_parser._can_handle(context)


@pytest.mark.asyncio
async def test_heading_with_extra_whitespace_should_work(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "#   Heading with extra spaces"

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_heading_with_tab_separator_should_work(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "##\tHeading with tab"

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_heading_without_space_should_not_be_handled(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "#NoHeading"

    assert not heading_parser._can_handle(context)


@pytest.mark.asyncio
async def test_heading_with_only_hashes_should_not_create_block(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "###   "

    if heading_parser._can_handle(context):
        await heading_parser._process(context)
        assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_heading_inside_parent_context_should_not_be_handled(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "# Heading"
    context.is_inside_parent_context = Mock(return_value=True)

    assert not heading_parser._can_handle(context)


@pytest.mark.asyncio
async def test_heading_with_inline_markdown_should_convert_rich_text(
    mock_rich_text_converter: MarkdownRichTextConverter, context: BlockParsingContext, syntax_registry: SyntaxRegistry
) -> None:
    parser = HeadingParser(rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry)
    context.line = "# **Bold** and *italic*"

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("**Bold** and *italic*")


@pytest.mark.asyncio
async def test_heading_with_trailing_whitespace_should_be_trimmed(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "## Heading with trailing spaces   "

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_heading_with_special_characters_should_work(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "# Heading with special chars äöü and emoji 🎉"

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_not_a_heading_should_not_be_handled(heading_parser: HeadingParser, context: BlockParsingContext) -> None:
    context.line = "Normal text without heading"

    assert not heading_parser._can_handle(context)


@pytest.mark.asyncio
async def test_heading_with_leading_whitespace_should_not_be_handled(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "  # Heading with leading space"

    assert not heading_parser._can_handle(context)


@pytest.mark.asyncio
async def test_multiple_hashes_in_content_should_work(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "# C# and #hashtags in text"

    assert heading_parser._can_handle(context)
    await heading_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_heading_data_should_have_correct_defaults(
    heading_parser: HeadingParser, context: BlockParsingContext
) -> None:
    context.line = "# Test Heading"

    await heading_parser._process(context)

    block = context.result_blocks[0]
    heading_data = block.heading_1

    assert heading_data.color == "default"
    assert heading_data.is_toggleable is False
