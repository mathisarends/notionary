from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import (
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.toggleable_heading import ToggleableHeadingParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def toggleable_heading_parser(
    mock_rich_text_converter: MarkdownRichTextConverter, syntax_registry: SyntaxRegistry
) -> ToggleableHeadingParser:
    return ToggleableHeadingParser(syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter)


@pytest.mark.parametrize(
    "line,expected_block_type",
    [
        ("+++ # Heading Level 1", CreateHeading1Block),
        ("+++ ## Heading Level 2", CreateHeading2Block),
        ("+++ ### Heading Level 3", CreateHeading3Block),
    ],
)
@pytest.mark.asyncio
async def test_heading_start_should_push_correct_block_to_parent_stack(
    toggleable_heading_parser: ToggleableHeadingParser,
    context: BlockParsingContext,
    line: str,
    expected_block_type: type,
) -> None:
    context.line = line

    assert toggleable_heading_parser._can_handle(context)
    await toggleable_heading_parser._process(context)

    assert len(context.parent_stack) == 1
    assert isinstance(context.parent_stack[0].block, expected_block_type)


@pytest.mark.asyncio
async def test_heading_level_1_should_create_heading1_block(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ # Heading Level 3"

    await toggleable_heading_parser._process(context)

    assert isinstance(context.parent_stack[0].block, CreateHeading1Block)


@pytest.mark.asyncio
async def test_heading_level_2_should_create_heading2_block(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ ## Heading Level 2"

    await toggleable_heading_parser._process(context)

    assert isinstance(context.parent_stack[0].block, CreateHeading2Block)


@pytest.mark.asyncio
async def test_heading_level_3_should_create_heading3_block(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ ### Heading Level 3"

    await toggleable_heading_parser._process(context)

    assert isinstance(context.parent_stack[0].block, CreateHeading3Block)


@pytest.mark.asyncio
async def test_heading_end_should_finalize_and_add_to_results(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ # Test Heading"
    await toggleable_heading_parser._process(context)

    context.line = "+++"
    await toggleable_heading_parser._process(context)

    assert len(context.parent_stack) == 0
    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateHeading1Block)


@pytest.mark.asyncio
async def test_heading_content_should_be_added_to_child_lines(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ # Test Heading"
    await toggleable_heading_parser._process(context)

    context.line = "This is content inside the heading"
    await toggleable_heading_parser._process(context)

    assert len(context.parent_stack[0].child_lines) == 1
    assert context.parent_stack[0].child_lines[0] == "This is content inside the heading"


@pytest.mark.asyncio
async def test_heading_with_multiple_content_lines_should_collect_all(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ # Test Heading"
    await toggleable_heading_parser._process(context)

    context.line = "First line"
    await toggleable_heading_parser._process(context)

    context.line = "Second line"
    await toggleable_heading_parser._process(context)

    assert len(context.parent_stack[0].child_lines) == 2


@pytest.mark.asyncio
async def test_heading_is_toggleable_should_be_true(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ # Test Heading"
    await toggleable_heading_parser._process(context)

    context.line = "+++"
    await toggleable_heading_parser._process(context)

    block = context.result_blocks[0]
    assert block.heading_1.is_toggleable is True


@pytest.mark.asyncio
async def test_heading_without_start_marker_should_not_be_handled(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "# Regular Heading"

    assert not toggleable_heading_parser._can_handle(context)


@pytest.mark.asyncio
async def test_end_marker_without_heading_on_stack_should_not_be_handled(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++"

    assert not toggleable_heading_parser._can_handle(context)


@pytest.mark.asyncio
async def test_heading_with_inline_markdown_should_convert_rich_text(
    mock_rich_text_converter: MarkdownRichTextConverter, context: BlockParsingContext, syntax_registry: SyntaxRegistry
) -> None:
    parser = ToggleableHeadingParser(rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry)
    context.line = "+++ # **Bold** and *italic*"

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("**Bold** and *italic*")


@pytest.mark.asyncio
async def test_heading_level_4_should_not_create_block(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ #### Invalid Level"

    await toggleable_heading_parser._process(context)

    assert len(context.parent_stack) == 0


@pytest.mark.asyncio
async def test_heading_with_empty_content_should_not_create_block(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++ #   "

    await toggleable_heading_parser._process(context)

    assert len(context.parent_stack) == 0


@pytest.mark.asyncio
async def test_nested_content_should_be_parsed(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.parse_nested_markdown = AsyncMock(return_value=[Mock()])

    context.line = "+++ # Heading"
    await toggleable_heading_parser._process(context)

    context.line = "Nested content"
    await toggleable_heading_parser._process(context)

    context.line = "+++"
    await toggleable_heading_parser._process(context)

    context.parse_nested_markdown.assert_called_once()


@pytest.mark.asyncio
async def test_heading_with_extra_whitespace_should_work(
    toggleable_heading_parser: ToggleableHeadingParser, context: BlockParsingContext
) -> None:
    context.line = "+++   #   Heading with spaces   "

    assert toggleable_heading_parser._can_handle(context)
    await toggleable_heading_parser._process(context)

    assert len(context.parent_stack) == 1
