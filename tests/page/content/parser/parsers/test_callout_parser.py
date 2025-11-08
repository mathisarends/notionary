from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.schemas import CreateCalloutBlock
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.context import BlockParsingContext
from notionary.page.content.parser.parsers.callout import CalloutParser


@pytest.fixture
def mock_rich_text_converter() -> AsyncMock:
    converter = AsyncMock()
    converter.to_rich_text = AsyncMock(
        return_value=[{"type": "text", "text": {"content": "test"}}]
    )
    return converter


@pytest.fixture
def callout_parser(
    syntax_registry: SyntaxDefinitionRegistry, mock_rich_text_converter: AsyncMock
) -> CalloutParser:
    return CalloutParser(
        syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter
    )


@pytest.fixture
def make_callout_syntax(syntax_registry: SyntaxDefinitionRegistry):
    syntax = syntax_registry.get_callout_syntax()

    def _make(content: str, emoji: str = "💡") -> str:
        return f'{syntax.start_delimiter}({content} "{emoji}"{syntax.end_delimiter}'

    return _make


@pytest.mark.asyncio
async def test_valid_callout_syntax_should_create_callout_block(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    context.line = make_callout_syntax("This is a callout")

    await callout_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateCalloutBlock)
    assert context.result_blocks[0].callout.icon.emoji == "💡"


@pytest.mark.asyncio
async def test_callout_with_custom_emoji_should_be_handled(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    context.line = make_callout_syntax("Important note", emoji="⚠️")

    await callout_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.callout.icon.emoji == "⚠️"


@pytest.mark.asyncio
async def test_callout_with_different_emojis_should_set_correct_emoji(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    emojis = ["💡", "⚠️", "✅", "❌", "ℹ️"]

    for emoji in emojis:
        context.line = make_callout_syntax("Test", emoji=emoji)
        context.result_blocks = []

        await callout_parser._process(context)

        assert len(context.result_blocks) == 1
        assert context.result_blocks[0].callout.icon.emoji == emoji


@pytest.mark.asyncio
async def test_callout_with_rich_text_content_should_convert(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    content = "**Bold** and *italic* content"
    context.line = make_callout_syntax(content)

    await callout_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].callout.rich_text is not None
    callout_parser._rich_text_converter.to_rich_text.assert_called()


@pytest.mark.asyncio
async def test_callout_without_custom_emoji_should_use_default(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
) -> None:
    context.line = '[callout](Default emoji callout "💡")'

    await callout_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].callout.icon.emoji == "💡"


def test_valid_callout_should_be_handled(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    context.line = make_callout_syntax("This should be handled")

    can_handle = callout_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.parametrize(
    "invalid_line",
    [
        "callout This is not valid syntax",
        "This is just regular text without callout",
        "Just some random content",
    ],
)
def test_invalid_callout_syntax_should_not_be_handled(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    invalid_line: str,
) -> None:
    context.line = invalid_line

    can_handle = callout_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_callout_with_special_characters_in_content_should_work(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    content = "Content with special chars: !@#$%^&*()"
    context.line = make_callout_syntax(content)

    await callout_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateCalloutBlock)


@pytest.mark.asyncio
async def test_callout_should_initialize_with_empty_children(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    context.line = make_callout_syntax("Callout with empty children")
    context.collect_indented_child_lines = Mock(return_value=[])

    await callout_parser._process(context)

    block = context.result_blocks[0]
    assert hasattr(block.callout, "children")
    assert block.callout.children == []


@pytest.mark.asyncio
async def test_callout_with_whitespace_should_be_trimmed(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
) -> None:
    context.line = '[callout](    Content with leading spaces    "💡")'

    await callout_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateCalloutBlock)


@pytest.mark.asyncio
async def test_callout_inside_parent_context_should_add_as_child(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    parent_block = Mock()
    parent_block.add_child_block = Mock()
    context.parent_stack = [parent_block]
    context.line = make_callout_syntax("Nested callout")
    context.collect_indented_child_lines = Mock(return_value=[])

    await callout_parser._process(context)

    # Should add to parent block instead of result_blocks
    assert len(context.result_blocks) == 0
    parent_block.add_child_block.assert_called_once()


@pytest.mark.asyncio
async def test_callout_should_append_block_to_result_blocks(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    context.line = make_callout_syntax("Content")
    initial_length = len(context.result_blocks)

    await callout_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1


@pytest.mark.asyncio
async def test_callout_block_should_have_correct_structure(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    context.line = make_callout_syntax("Test content")

    await callout_parser._process(context)

    block = context.result_blocks[0]
    assert hasattr(block, "callout")
    assert hasattr(block.callout, "rich_text")
    assert hasattr(block.callout, "icon")
    assert hasattr(block.callout, "children")
    assert hasattr(block.callout.icon, "emoji")


@pytest.mark.asyncio
async def test_multiple_callouts_in_sequence_should_create_separate_blocks(
    callout_parser: CalloutParser,
    context: BlockParsingContext,
    make_callout_syntax,
) -> None:
    callout1 = make_callout_syntax("First callout", emoji="💡")
    callout2 = make_callout_syntax("Second callout", emoji="⚠️")
    context.collect_indented_child_lines = Mock(return_value=[])

    context.line = callout1
    await callout_parser._process(context)

    context.line = callout2
    await callout_parser._process(context)

    assert len(context.result_blocks) == 2
    assert context.result_blocks[0].callout.icon.emoji == "💡"
    assert context.result_blocks[1].callout.icon.emoji == "⚠️"
