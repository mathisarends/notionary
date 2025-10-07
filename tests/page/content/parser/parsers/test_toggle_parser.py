from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import BlockColor, CreateToggleBlock, CreateToggleData
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.toggle import ToggleParser


@pytest.fixture
def toggle_parser(mock_rich_text_converter: MarkdownRichTextConverter) -> ToggleParser:
    return ToggleParser(rich_text_converter=mock_rich_text_converter)


@pytest.mark.asyncio
async def test_toggle_start_should_push_to_parent_stack(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"

    assert toggle_parser._can_handle(context)
    await toggle_parser._process(context)

    assert len(context.parent_stack) == 1
    assert isinstance(context.parent_stack[0].block, CreateToggleBlock)


@pytest.mark.asyncio
async def test_toggle_end_should_finalize_and_add_to_results(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"
    await toggle_parser._process(context)

    context.line = "+++"
    await toggle_parser._process(context)

    assert len(context.parent_stack) == 0
    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateToggleBlock)


@pytest.mark.asyncio
async def test_toggle_content_should_be_added_to_child_lines(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"
    await toggle_parser._process(context)

    context.line = "This is content inside toggle"
    await toggle_parser._process(context)

    assert len(context.parent_stack[0].child_lines) == 1
    assert context.parent_stack[0].child_lines[0] == "This is content inside toggle"


@pytest.mark.asyncio
async def test_toggle_with_multiple_content_lines_should_collect_all(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"
    await toggle_parser._process(context)

    context.line = "First line"
    await toggle_parser._process(context)

    context.line = "Second line"
    await toggle_parser._process(context)

    assert len(context.parent_stack[0].child_lines) == 2


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
    mock_rich_text_converter: MarkdownRichTextConverter, context: BlockParsingContext
) -> None:
    parser = ToggleParser(rich_text_converter=mock_rich_text_converter)
    context.line = "+++ **Bold** and *italic* title"

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("**Bold** and *italic* title")


@pytest.mark.asyncio
async def test_nested_toggle_in_parent_context_should_add_to_parent(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    parent_toggle = Mock()
    toggle_data = CreateToggleData(rich_text=[], color=BlockColor.DEFAULT, children=[])
    parent_toggle.block = CreateToggleBlock(toggle=toggle_data)
    parent_toggle.add_child_block = Mock()
    context.parent_stack.append(parent_toggle)

    context.line = "+++ Nested Toggle"
    await toggle_parser._process(context)

    context.line = "+++"
    await toggle_parser._process(context)

    parent_toggle.add_child_block.assert_called_once()
    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_toggle_without_parent_should_add_to_results(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++ Toggle Title"
    await toggle_parser._process(context)

    context.line = "+++"
    await toggle_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_end_marker_without_toggle_on_stack_should_not_be_handled(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++"

    assert not toggle_parser._can_handle(context)


@pytest.mark.asyncio
async def test_nested_content_should_be_parsed(toggle_parser: ToggleParser, context: BlockParsingContext) -> None:
    context.parse_nested_content = AsyncMock(return_value=[Mock()])

    context.line = "+++ Toggle Title"
    await toggle_parser._process(context)

    context.line = "Nested content"
    await toggle_parser._process(context)

    context.line = "+++"
    await toggle_parser._process(context)

    context.parse_nested_content.assert_called_once()


@pytest.mark.asyncio
async def test_toggle_with_empty_content_should_have_empty_children(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.parse_nested_content = AsyncMock(return_value=[])

    context.line = "+++ Toggle Title"
    await toggle_parser._process(context)

    context.line = "+++"
    await toggle_parser._process(context)

    block = context.result_blocks[0]
    assert block.toggle.children == []


@pytest.mark.asyncio
async def test_is_heading_start_with_heading_pattern_should_return_true(toggle_parser: ToggleParser) -> None:
    assert toggle_parser.is_heading_start("+++ # Heading")
    assert toggle_parser.is_heading_start("+++ ## Heading")
    assert toggle_parser.is_heading_start("+++ ### Heading")


@pytest.mark.asyncio
async def test_is_heading_start_with_toggle_pattern_should_return_false(toggle_parser: ToggleParser) -> None:
    assert not toggle_parser.is_heading_start("+++ Toggle Title")


@pytest.mark.asyncio
async def test_toggle_with_extra_whitespace_should_work(
    toggle_parser: ToggleParser, context: BlockParsingContext
) -> None:
    context.line = "+++   Toggle with spaces   "

    assert toggle_parser._can_handle(context)
    await toggle_parser._process(context)

    assert len(context.parent_stack) == 1
