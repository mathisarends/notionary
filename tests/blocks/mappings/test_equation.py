import pytest

from notionary.blocks.mappings.equation import EquationMapper
from notionary.blocks.schemas import (
    BlockType,
    CreateEquationBlock,
    EquationBlock,
    EquationData,
    PartialUserDto,
)


def create_equation_block_with_required_fields(expression: str = "E = mc^2", **kwargs) -> EquationBlock:
    """Helper to create EquationBlock with all required BaseBlock fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "type": BlockType.EQUATION,
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": PartialUserDto(object="user", id="user-id"),
        "last_edited_by": PartialUserDto(object="user", id="user-id"),
        "equation": EquationData(expression=expression),
    }
    defaults.update(kwargs)
    return EquationBlock(**defaults)


@pytest.mark.asyncio
async def test_match_markdown_valid_simple():
    """Test recognition of valid simple equation syntax."""
    assert await EquationMapper.markdown_to_notion("$$E = mc^2$$")
    assert await EquationMapper.markdown_to_notion("$$x + y = z$$")
    assert await EquationMapper.markdown_to_notion("$$a = b$$")
    assert await EquationMapper.markdown_to_notion("  $$simple$$  ")  # With spaces


@pytest.mark.asyncio
async def test_match_markdown_valid_complex():
    """Test recognition of valid complex equation syntax."""
    assert await EquationMapper.markdown_to_notion("$$\\frac{a}{b}$$")
    assert await EquationMapper.markdown_to_notion("$$\\sum_{i=1}^n i$$")
    assert await EquationMapper.markdown_to_notion("$$\\int_0^\\infty e^{-x} dx$$")


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert await EquationMapper.markdown_to_notion("$E = mc^2$") is None  # Single $
    assert await EquationMapper.markdown_to_notion("$$$$") is None  # Empty
    assert await EquationMapper.markdown_to_notion("$$   $$") is None  # Only whitespace
    assert await EquationMapper.markdown_to_notion("E = mc^2") is None  # No $$
    assert await EquationMapper.markdown_to_notion("") is None  # Empty string


def test_match_notion_valid():
    """Test recognition of valid equation blocks."""
    block = create_equation_block_with_required_fields(expression="E = mc^2")
    assert EquationMapper.match_notion(block)


def test_match_notion_invalid():
    """Test rejection of invalid blocks."""
    # Wrong type - use Mock
    from unittest.mock import Mock

    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.equation = EquationData(expression="E = mc^2")
    assert not EquationMapper.match_notion(paragraph_block)

    # Right type but no equation - use Mock
    no_equation_block = Mock()
    no_equation_block.type = BlockType.EQUATION
    no_equation_block.equation = None
    assert not EquationMapper.match_notion(no_equation_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_simple():
    """Test conversion from simple markdown to Notion blocks."""
    result = await EquationMapper.markdown_to_notion("$$E = mc^2$$")

    assert isinstance(result, CreateEquationBlock)
    assert isinstance(result.equation, EquationData)
    assert result.equation.expression == "E = mc^2"


@pytest.mark.asyncio
async def test_markdown_to_notion_complex():
    """Test conversion from complex markdown to Notion blocks."""
    result = await EquationMapper.markdown_to_notion("$$\\frac{a}{b}$$")

    assert isinstance(result, CreateEquationBlock)
    assert isinstance(result.equation, EquationData)
    assert result.equation.expression == "\\frac{a}{b}"


@pytest.mark.asyncio
async def test_markdown_to_notion_multiline():
    """Test conversion with multiline expressions."""
    result = await EquationMapper.markdown_to_notion("$$a = b\nc = d$$")

    assert isinstance(result, CreateEquationBlock)
    assert isinstance(result.equation, EquationData)
    assert result.equation.expression == "a = b\nc = d"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await EquationMapper.markdown_to_notion("$E = mc^2$") is None  # Single $
    assert await EquationMapper.markdown_to_notion("$$$$") is None  # Empty
    assert await EquationMapper.markdown_to_notion("E = mc^2") is None  # No $$
    assert await EquationMapper.markdown_to_notion("") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_simple():
    """Test conversion from simple Notion blocks to markdown."""
    block = create_equation_block_with_required_fields(expression="E = mc^2")

    result = await EquationMapper.notion_to_markdown(block)
    assert result == "$$E = mc^2$$"


@pytest.mark.asyncio
async def test_notion_to_markdown_complex():
    """Test conversion with complex expressions."""
    block = create_equation_block_with_required_fields(expression="\\frac{a}{b}")

    result = await EquationMapper.notion_to_markdown(block)
    assert result == "$$\\frac{a}{b}$$"


@pytest.mark.asyncio
async def test_notion_to_markdown_multiline():
    """Test conversion with multiline expressions."""
    block = create_equation_block_with_required_fields(expression="a = b\nc = d")

    result = await EquationMapper.notion_to_markdown(block)
    assert result == "$$a = b\nc = d$$"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    # Wrong type - use Mock
    from unittest.mock import Mock

    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.equation = EquationData(expression="E = mc^2")
    assert await EquationMapper.notion_to_markdown(paragraph_block) is None

    # Right type but no equation - use Mock
    no_equation_block = Mock()
    no_equation_block.type = BlockType.EQUATION
    no_equation_block.equation = None
    assert await EquationMapper.notion_to_markdown(no_equation_block) is None

    # Empty expression
    empty_equation_block = create_equation_block_with_required_fields(expression="")
    assert await EquationMapper.notion_to_markdown(empty_equation_block) is None


@pytest.mark.asyncio
async def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "$$E = mc^2$$",
        "$$\\frac{a}{b}$$",
        "$$\\sum_{i=1}^n i = \\frac{n(n+1)}{2}$$",
        "$$\\int_0^\\infty e^{-x^2} dx$$",
    ]

    for markdown in test_cases:
        # Convert to notion
        notion_result = await EquationMapper.markdown_to_notion(markdown)
        assert notion_result is not None

        # Create proper Block with the equation data for roundtrip
        notion_block = create_equation_block_with_required_fields(expression=notion_result.equation.expression)

        # Convert back to markdown
        back_to_markdown = await EquationMapper.notion_to_markdown(notion_block)
        assert back_to_markdown == markdown


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression",
    [
        "E = mc^2",
        "\\frac{a}{b}",
        "\\sum_{i=1}^n i",
        "\\int_0^\\infty e^{-x} dx",
        "x^2 + y^2 = z^2",
        "\\alpha + \\beta = \\gamma",
    ],
)
async def test_various_expressions(expression):
    """Test various LaTeX expressions."""
    markdown = f"$${expression}$$"
    result = await EquationMapper.markdown_to_notion(markdown)
    assert result is not None
    assert result.equation.expression == expression
