"""
Pytest tests for EquationElement.
Tests the essential functionality for equation block handling.
"""

from notionary.blocks.equation.equation_element import EquationElement
from notionary.blocks.equation.equation_models import (
    EquationBlock,
    CreateEquationBlock,
)
from notionary.blocks.block_models import Block, BlockType


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"},
    }
    defaults.update(kwargs)
    return Block(**defaults)


def test_match_markdown_valid_unquoted():
    """Test recognition of valid unquoted equation syntax."""
    assert EquationElement.markdown_to_notion("[equation](E = mc^2)")
    assert EquationElement.markdown_to_notion("[equation](x + y = z)")
    assert EquationElement.markdown_to_notion("[equation](a = b)")
    assert EquationElement.markdown_to_notion("  [equation](simple)  ")  # With spaces


def test_match_markdown_valid_quoted():
    """Test recognition of valid quoted equation syntax."""
    assert EquationElement.markdown_to_notion('[equation]("E = mc^2")')
    assert EquationElement.markdown_to_notion(
        '[equation]("f(x) = sin(x)")'
    )  # With parentheses
    assert EquationElement.markdown_to_notion(
        '[equation]("x = a\\ny = b")'
    )  # With newlines
    assert EquationElement.markdown_to_notion(
        '[equation]("say \\"hello\\"")'
    )  # With escaped quotes


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not EquationElement.markdown_to_notion("[equation]")  # Missing expression
    assert not EquationElement.markdown_to_notion(
        "equation(E = mc^2)"
    )  # Missing brackets
    assert not EquationElement.markdown_to_notion(
        "[eq](E = mc^2)"
    )  # Wrong element name
    assert not EquationElement.markdown_to_notion(
        "[equation](E = mc^2"
    )  # Missing closing paren
    assert not EquationElement.markdown_to_notion(
        "[equation]E = mc^2)"
    )  # Missing opening paren
    assert not EquationElement.markdown_to_notion("[toc](blue)")  # Different element
    assert not EquationElement.markdown_to_notion("")  # Empty string


def test_match_notion_valid():
    """Test recognition of valid equation blocks."""
    block = create_block_with_required_fields(
        type=BlockType.EQUATION, equation=EquationBlock(expression="E = mc^2")
    )
    assert EquationElement.match_notion(block)


def test_match_notion_invalid():
    """Test rejection of invalid blocks."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH, equation=EquationBlock(expression="E = mc^2")
    )
    assert not EquationElement.match_notion(paragraph_block)

    # Right type but no equation
    no_equation_block = create_block_with_required_fields(
        type=BlockType.EQUATION, equation=None
    )
    assert not EquationElement.match_notion(no_equation_block)


def test_markdown_to_notion_unquoted():
    """Test conversion from unquoted markdown to Notion blocks."""
    result = EquationElement.markdown_to_notion("[equation](E = mc^2)")

    assert isinstance(result, CreateEquationBlock)
    assert isinstance(result.equation, EquationBlock)
    assert result.equation.expression == "E = mc^2"


def test_markdown_to_notion_quoted():
    """Test conversion from quoted markdown to Notion blocks."""
    result = EquationElement.markdown_to_notion('[equation]("f(x) = sin(x)")')

    assert isinstance(result, CreateEquationBlock)
    assert isinstance(result.equation, EquationBlock)
    assert result.equation.expression == "f(x) = sin(x)"


def test_markdown_to_notion_quoted_with_escaping():
    """Test conversion with escaped characters."""
    result = EquationElement.markdown_to_notion('[equation]("\\\\frac{a}{b}")')

    assert isinstance(result, CreateEquationBlock)
    assert isinstance(result.equation, EquationBlock)
    # Should be unescaped in Notion
    assert result.equation.expression == "\\frac{a}{b}"


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert EquationElement.markdown_to_notion("[equation]") is None
    assert EquationElement.markdown_to_notion("equation(E = mc^2)") is None
    assert EquationElement.markdown_to_notion("[toc](blue)") is None
    assert EquationElement.markdown_to_notion("") is None


def test_markdown_to_notion_empty_expression():
    """Test that empty expressions return None."""
    assert EquationElement.markdown_to_notion("[equation]()") is None
    assert EquationElement.markdown_to_notion('[equation]("")') is None
    assert EquationElement.markdown_to_notion('[equation]("   ")') is None


def test_notion_to_markdown_simple():
    """Test conversion from simple Notion blocks to unquoted markdown."""
    block = create_block_with_required_fields(
        type=BlockType.EQUATION, equation=EquationBlock(expression="E = mc^2")
    )

    result = EquationElement.notion_to_markdown(block)
    assert result == "[equation](E = mc^2)"


def test_notion_to_markdown_with_parentheses():
    """Test conversion with parentheses forces quoted form."""
    block = create_block_with_required_fields(
        type=BlockType.EQUATION, equation=EquationBlock(expression="f(x) = sin(x)")
    )

    result = EquationElement.notion_to_markdown(block)
    assert result == '[equation]("f(x) = sin(x)")'


def test_notion_to_markdown_with_quotes():
    """Test conversion with quotes forces quoted form and escaping."""
    block = create_block_with_required_fields(
        type=BlockType.EQUATION, equation=EquationBlock(expression='say "hello"')
    )

    result = EquationElement.notion_to_markdown(block)
    assert result == '[equation]("say \\"hello\\"")'


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH, equation=EquationBlock(expression="E = mc^2")
    )
    assert EquationElement.notion_to_markdown(paragraph_block) is None

    # Right type but no equation
    no_equation_block = create_block_with_required_fields(
        type=BlockType.EQUATION, equation=None
    )
    assert EquationElement.notion_to_markdown(no_equation_block) is None

    # Empty expression
    empty_equation_block = create_block_with_required_fields(
        type=BlockType.EQUATION, equation=EquationBlock(expression="")
    )
    assert EquationElement.notion_to_markdown(empty_equation_block) is None
