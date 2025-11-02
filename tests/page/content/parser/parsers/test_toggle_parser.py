from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.schemas import CreateToggleBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.toggle import ToggleParser
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_to_rich_text.service import (
    MarkdownRichTextConverter,
)


@pytest.fixture
def toggle_parser(
    mock_rich_text_converter: MarkdownRichTextConverter,
    syntax_registry: SyntaxDefinitionRegistry,
) -> ToggleParser:
    return ToggleParser(
        syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter
    )


@pytest.mark.asyncio
async def test_toggle_start_should_process_immediately(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"
    context.remaining_lines = []

    assert toggle_parser._can_handle(context)
    await toggle_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateToggleBlock)


@pytest.mark.asyncio
async def test_toggle_with_indented_children_should_collect_them(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(
        return_value=["    First line", "    Second line"]
    )
    context.strip_indentation_level = Mock(return_value=["First line", "Second line"])
    context.parse_nested_markdown = AsyncMock(return_value=[Mock(), Mock()])

    await toggle_parser._process(context)

    # Should have collected and processed the indented lines
    context.collect_indented_child_lines.assert_called_once_with(0)
    context.parse_nested_markdown.assert_called_once_with("First line\nSecond line")

    # Should have marked lines as consumed
    assert context.lines_consumed == 2
    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_toggle_without_children_should_create_empty_toggle(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await toggle_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.toggle.children == []
    assert context.lines_consumed == 0


@pytest.mark.parametrize(
    "line",
    [
        "+++ # Heading Level 1",
        "+++ ## Heading Level 2",
        "+++ ### Heading Level 3",
    ],
)
@pytest.mark.asyncio
async def test_toggleable_heading_pattern_should_not_be_handled(
    toggle_parser: ToggleParser, context: BlockParsingContext, line: str
) -> None:
    context.line = line

    assert not toggle_parser._can_handle(context)


@pytest.mark.asyncio
async def test_toggle_with_inline_markdown_should_convert_rich_text(
    mock_rich_text_converter: MarkdownRichTextConverter,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    parser = ToggleParser(
        rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry
    )
    context.line = "+++ **Bold** and *italic* title"
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with(
        "**Bold** and *italic* title"
    )


@pytest.mark.asyncio
async def test_toggle_with_extra_whitespace_should_work(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++   Toggle with spaces   "
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    assert toggle_parser._can_handle(context)
    await toggle_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_is_heading_start_with_heading_pattern_should_return_true(
    toggle_parser: ToggleParser,
) -> None:
    assert toggle_parser.is_heading_start("+++ # Heading")
    assert toggle_parser.is_heading_start("+++ ## Heading")
    assert toggle_parser.is_heading_start("+++ ### Heading")


@pytest.mark.asyncio
async def test_is_heading_start_with_toggle_pattern_should_return_false(
    toggle_parser: ToggleParser,
) -> None:
    assert not toggle_parser.is_heading_start("+++ Toggle Title")
