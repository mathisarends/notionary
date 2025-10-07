from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.page.content.parser.parsers.base import BlockParsingContext


@pytest.fixture
def mock_rich_text_converter() -> MarkdownRichTextConverter:
    converter: MarkdownRichTextConverter = AsyncMock(spec=MarkdownRichTextConverter)
    converter.to_rich_text = AsyncMock(return_value=[{"type": "text", "text": {"content": "test"}}])
    return converter


@pytest.fixture
def context() -> BlockParsingContext:
    ctx: BlockParsingContext = Mock(spec=BlockParsingContext)
    ctx.result_blocks = []
    ctx.is_inside_parent_context = Mock(return_value=False)
    return ctx
