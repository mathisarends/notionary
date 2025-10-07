from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import EquationBlock, EquationData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.equation import EquationRenderer


def _create_equation_data(expression: str) -> EquationData:
    return EquationData(expression=expression)


def _create_equation_block(equation_data: EquationData | None) -> EquationBlock:
    block = Mock(spec=EquationBlock)
    block.type = BlockType.EQUATION
    block.equation = equation_data
    return block


@pytest.fixture
def equation_renderer() -> EquationRenderer:
    return EquationRenderer()


@pytest.mark.asyncio
async def test_equation_block_should_be_handled(equation_renderer: EquationRenderer, mock_block: EquationBlock) -> None:
    mock_block.type = BlockType.EQUATION

    assert equation_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_equation_block_should_not_be_handled(
    equation_renderer: EquationRenderer, mock_block: EquationBlock
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not equation_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_equation_with_expression_should_render_latex(
    equation_renderer: EquationRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    equation_data = _create_equation_data("E = mc^2")
    block = _create_equation_block(equation_data)
    render_context.block = block

    await equation_renderer._process(render_context)

    assert render_context.markdown_result == "$$E = mc^2$$"


@pytest.mark.asyncio
async def test_equation_with_complex_expression_should_render_latex(
    equation_renderer: EquationRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    equation_data = _create_equation_data(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}")
    block = _create_equation_block(equation_data)
    render_context.block = block

    await equation_renderer._process(render_context)

    assert "$$" in render_context.markdown_result
    assert r"\int_0^\infty" in render_context.markdown_result


@pytest.mark.asyncio
async def test_equation_with_empty_expression_should_render_empty_string(
    equation_renderer: EquationRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    equation_data = _create_equation_data("")
    block = _create_equation_block(equation_data)
    render_context.block = block

    await equation_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_equation_with_missing_data_should_render_empty_string(
    equation_renderer: EquationRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_equation_block(None)
    render_context.block = block

    await equation_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_equation_with_indent_level_should_indent_output(
    equation_renderer: EquationRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    equation_data = _create_equation_data("x^2 + y^2 = r^2")
    block = _create_equation_block(equation_data)
    render_context.block = block
    render_context.indent_level = 1

    await equation_renderer._process(render_context)

    render_context.indent_text.assert_called_once()
    assert render_context.markdown_result == "  $$x^2 + y^2 = r^2$$"


@pytest.mark.asyncio
async def test_equation_with_children_should_render_children_with_indent(
    equation_renderer: EquationRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    equation_data = _create_equation_data("a^2 + b^2 = c^2")
    block = _create_equation_block(equation_data)
    render_context.block = block
    render_context.render_children_with_additional_indent = AsyncMock(return_value="  Child content")

    await equation_renderer._process(render_context)

    render_context.render_children_with_additional_indent.assert_called_once_with(1)
    assert "$$a^2 + b^2 = c^2$$" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_extract_equation_expression_with_valid_data_should_return_expression(
    equation_renderer: EquationRenderer,
) -> None:
    equation_data = _create_equation_data("f(x) = x^2")
    block = _create_equation_block(equation_data)

    expression = equation_renderer._extract_equation_expression(block)

    assert expression == "f(x) = x^2"


@pytest.mark.asyncio
async def test_extract_equation_expression_without_data_should_return_empty_string(
    equation_renderer: EquationRenderer,
) -> None:
    block = _create_equation_block(None)

    expression = equation_renderer._extract_equation_expression(block)

    assert expression == ""
