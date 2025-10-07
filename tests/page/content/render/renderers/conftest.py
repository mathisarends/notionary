from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext


@pytest.fixture
def mock_rich_text_markdown_converter() -> RichTextToMarkdownConverter:
    converter: RichTextToMarkdownConverter = AsyncMock(spec=RichTextToMarkdownConverter)
    converter.to_markdown = AsyncMock(return_value="converted markdown")
    return converter


@pytest.fixture
def mock_block() -> Block:
    block: Block = Mock(spec=Block)
    block.has_children = False
    block.children = []
    return block


@pytest.fixture
def render_context(mock_block: Block) -> MarkdownRenderingContext:
    context: MarkdownRenderingContext = Mock(spec=MarkdownRenderingContext)
    context.block = mock_block
    context.indent_level = 0
    context.markdown_result = ""
    context.indent_text = Mock(side_effect=lambda text: f"  {text}")
    context.render_children_with_additional_indent = AsyncMock(return_value="")
    return context
