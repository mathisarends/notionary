from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateEquationBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.equation import EquationParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def equation_parser(syntax_registry: SyntaxRegistry) -> EquationParser:
    return EquationParser(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_equation_should_create_equation_block(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "E = mc^2",
            "$$",
        ]
    )

    await equation_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateEquationBlock)
    assert block.equation.expression == "E = mc^2"


@pytest.mark.asyncio
async def test_multi_line_equation_should_join_with_newlines(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "\\int_{a}^{b} f(x) dx",
            "= F(b) - F(a)",
            "$$",
        ]
    )

    await equation_parser._process(context)

    block = context.result_blocks[0]
    assert block.equation.expression == "\\int_{a}^{b} f(x) dx\n= F(b) - F(a)"


@pytest.mark.asyncio
async def test_equation_should_consume_correct_number_of_lines(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "x^2 + y^2 = z^2",
            "$$",
            "Not part of equation",
        ]
    )

    await equation_parser._process(context)

    assert context.lines_consumed == 2


@pytest.mark.asyncio
async def test_multi_line_equation_should_consume_all_lines_until_closing_delimiter(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "First line",
            "Second line",
            "Third line",
            "$$",
        ]
    )

    await equation_parser._process(context)

    assert context.lines_consumed == 4


@pytest.mark.asyncio
async def test_equation_with_whitespace_in_content_should_preserve(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "  x = 5  ",
            "$$",
        ]
    )

    await equation_parser._process(context)

    block = context.result_blocks[0]
    assert block.equation.expression == "x = 5"


@pytest.mark.parametrize(
    "line",
    [
        "$$",
        "$$ ",
        "$$  ",
        "$$ \t",
    ],
)
def test_equation_delimiter_with_trailing_whitespace_should_handle(
    equation_parser: EquationParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = equation_parser._can_handle(context)

    assert can_handle is True


def test_equation_inside_parent_context_should_not_handle(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = equation_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "$ $",
        "$$$",
        " $$",
        "$$equation",
        "equation$$",
        "$",
    ],
)
def test_equation_with_invalid_delimiter_should_not_handle(
    equation_parser: EquationParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = equation_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_equation_with_empty_content_should_not_create_block(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "$$",
        ]
    )

    await equation_parser._process(context)

    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_equation_with_only_whitespace_content_should_not_create_block(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "   ",
            "$$",
        ]
    )

    await equation_parser._process(context)

    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_equation_without_closing_delimiter_should_consume_all_remaining_lines(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "x^2",
            "y^2",
        ]
    )

    await equation_parser._process(context)

    assert context.lines_consumed == 2


@pytest.mark.asyncio
async def test_equation_with_complex_latex_should_create_block(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}",
            "$$",
        ]
    )

    await equation_parser._process(context)

    block = context.result_blocks[0]
    assert block.equation.expression == "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}"


@pytest.mark.asyncio
async def test_equation_should_strip_surrounding_whitespace_from_expression(
    equation_parser: EquationParser,
    context: BlockParsingContext,
) -> None:
    context.line = "$$"
    context.get_remaining_lines = Mock(
        return_value=[
            "  ",
            "x = 5",
            "  ",
            "$$",
        ]
    )

    await equation_parser._process(context)

    block = context.result_blocks[0]
    assert block.equation.expression == "x = 5"
