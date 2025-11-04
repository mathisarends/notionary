from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.syntax.definition import (
    MarkdownGrammar,
    SyntaxDefinitionRegistry,
)


@pytest.fixture
def syntax_registry() -> SyntaxDefinitionRegistry:
    return SyntaxDefinitionRegistry()


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def indent(markdown_grammar: MarkdownGrammar) -> str:
    return " " * markdown_grammar.spaces_per_nesting_level


@pytest.fixture
def mock_rich_text_markdown_converter() -> RichTextToMarkdownConverter:
    mock_obj: RichTextToMarkdownConverter = AsyncMock(spec=RichTextToMarkdownConverter)
    converter = cast(RichTextToMarkdownConverter, mock_obj)
    converter.to_markdown = AsyncMock(return_value="converted markdown")
    return converter


@pytest.fixture
def mock_block() -> Block:
    mock_obj = Mock(spec=Block)
    block = cast(Block, mock_obj)
    block.has_children = False
    block.children = []
    return block


@pytest.fixture
def render_context(mock_block: Block) -> MarkdownRenderingContext:
    mock_obj: MarkdownRenderingContext = Mock(spec=MarkdownRenderingContext)
    context = cast(MarkdownRenderingContext, mock_obj)
    context.block = mock_block
    context.indent_level = 0
    context.markdown_result = ""
    context.indent_text = Mock(side_effect=lambda text: f"  {text}")
    context.render_children = AsyncMock(return_value="")
    context.render_children_with_additional_indent = AsyncMock(return_value="")
    return context
