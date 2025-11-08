from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CodingLanguage, CreateCodeBlock
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.code import CodeParser
from notionary.rich_text.markdown_to_rich_text.converter import (
    MarkdownRichTextConverter,
)


@pytest.fixture
def code_parser(
    mock_rich_text_converter: MarkdownRichTextConverter,
    syntax_registry: SyntaxDefinitionRegistry,
) -> CodeParser:
    return CodeParser(
        syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter
    )


def _setup_code_block_context(
    context: BlockParsingContext, code_lines: list[str]
) -> None:
    context.line = "```"
    context.get_remaining_lines = Mock(return_value=[*code_lines, "```"])


def _setup_code_block_context_with_language(
    context: BlockParsingContext, code_lines: list[str], language: str
) -> None:
    context.line = f"```{language}"
    context.get_remaining_lines = Mock(return_value=[*code_lines, "```"])


@pytest.mark.asyncio
async def test_code_block_should_create_code_block(
    code_parser: CodeParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    _setup_code_block_context(context, ["print('Hello World')"])

    await code_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateCodeBlock)
    assert block.code.language == CodingLanguage.PLAIN_TEXT
    assert block.code.caption == []
    mock_rich_text_converter.to_rich_text.assert_called_once_with(
        "print('Hello World')"
    )


@pytest.mark.parametrize(
    "language_tag,expected_language",
    [
        ("python", CodingLanguage.PYTHON),
        ("javascript", CodingLanguage.JAVASCRIPT),
        ("java", CodingLanguage.JAVA),
        ("typescript", CodingLanguage.TYPESCRIPT),
        ("c", CodingLanguage.C),
        ("cpp", CodingLanguage.CPP),
        ("go", CodingLanguage.GO),
        ("rust", CodingLanguage.RUST),
    ],
)
@pytest.mark.asyncio
async def test_code_block_with_language_should_set_correct_language(
    code_parser: CodeParser,
    context: BlockParsingContext,
    language_tag: str,
    expected_language: CodingLanguage,
) -> None:
    _setup_code_block_context_with_language(context, ["code"], language_tag)

    await code_parser._process(context)

    block = context.result_blocks[0]
    assert block.code.language == expected_language


@pytest.mark.asyncio
async def test_code_block_with_case_insensitive_language_should_parse(
    code_parser: CodeParser,
    context: BlockParsingContext,
) -> None:
    _setup_code_block_context_with_language(context, ["code"], "PYTHON")

    await code_parser._process(context)

    block = context.result_blocks[0]
    assert block.code.language == CodingLanguage.PYTHON


@pytest.mark.asyncio
async def test_code_block_with_unknown_language_should_use_plain_text(
    code_parser: CodeParser,
    context: BlockParsingContext,
) -> None:
    _setup_code_block_context_with_language(context, ["code"], "unknownlang")

    await code_parser._process(context)

    block = context.result_blocks[0]
    assert block.code.language == CodingLanguage.PLAIN_TEXT


@pytest.mark.asyncio
async def test_multi_line_code_should_join_with_newlines(
    code_parser: CodeParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    _setup_code_block_context_with_language(
        context,
        [
            "def hello():",
            "    print('Hello')",
            "    return True",
        ],
        "python",
    )

    await code_parser._process(context)

    expected_content = "def hello():\n    print('Hello')\n    return True"
    mock_rich_text_converter.to_rich_text.assert_called_once_with(expected_content)


@pytest.mark.asyncio
async def test_code_block_should_consume_correct_number_of_lines(
    code_parser: CodeParser,
    context: BlockParsingContext,
) -> None:
    _setup_code_block_context(
        context,
        [
            "line1",
            "line2",
        ],
    )
    context.get_remaining_lines = Mock(
        return_value=[
            "line1",
            "line2",
            "```",
            "not part of code",
        ]
    )

    await code_parser._process(context)

    assert context.lines_consumed == 3


@pytest.mark.asyncio
async def test_code_block_without_closing_fence_should_consume_all_lines(
    code_parser: CodeParser,
    context: BlockParsingContext,
) -> None:
    _setup_code_block_context(
        context,
        [
            "line1",
            "line2",
        ],
    )
    # Override to not include closing fence
    context.get_remaining_lines = Mock(
        return_value=[
            "line1",
            "line2",
        ]
    )

    await code_parser._process(context)

    assert context.lines_consumed == 2


@pytest.mark.asyncio
async def test_code_block_with_empty_content_should_create_block(
    code_parser: CodeParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    _setup_code_block_context(context, [])

    await code_parser._process(context)

    assert len(context.result_blocks) == 1
    mock_rich_text_converter.to_rich_text.assert_called_once_with("")


@pytest.mark.asyncio
async def test_code_block_should_preserve_indentation(
    code_parser: CodeParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    _setup_code_block_context_with_language(
        context,
        [
            "def hello():",
            "    print('indented')",
            "        print('more indented')",
        ],
        "python",
    )

    await code_parser._process(context)

    expected_content = (
        "def hello():\n    print('indented')\n        print('more indented')"
    )
    mock_rich_text_converter.to_rich_text.assert_called_once_with(expected_content)


@pytest.mark.parametrize(
    "line",
    [
        "```",
        "```python",
        "```javascript",
        "``` ",
        "```python ",
    ],
)
def test_code_fence_start_should_handle(
    code_parser: CodeParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = code_parser._can_handle(context)

    assert can_handle is True


def test_code_block_inside_parent_context_should_not_handle(
    code_parser: CodeParser,
    context: BlockParsingContext,
) -> None:
    context.line = "```"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = code_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "``",
        "`",
        "` ``",
        "```python code",
        "code ```",
        " ```",
        "````",
    ],
)
def test_code_fence_with_invalid_syntax_should_not_handle(
    code_parser: CodeParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = code_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_code_block_with_trailing_whitespace_on_fence_should_handle(
    code_parser: CodeParser,
    context: BlockParsingContext,
) -> None:
    context.line = "```  "
    context.get_remaining_lines = Mock(
        return_value=[
            "code",
            "```  ",
        ]
    )

    await code_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_code_block_should_append_block_to_result_blocks(
    code_parser: CodeParser,
    context: BlockParsingContext,
) -> None:
    _setup_code_block_context(context, ["code"])
    initial_length = len(context.result_blocks)

    await code_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1
