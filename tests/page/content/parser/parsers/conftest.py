from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.page.content.parser.parsers.base import BlockParsingContext


@pytest.fixture
def mock_rich_text_converter() -> MarkdownRichTextConverter:
    mock_obj = AsyncMock(spec=MarkdownRichTextConverter)
    converter = cast(MarkdownRichTextConverter, mock_obj)
    converter.to_rich_text = AsyncMock(return_value=[{"type": "text", "text": {"content": "test"}}])
    return converter


@pytest.fixture
def context() -> BlockParsingContext:
    mock_obj = Mock(spec=BlockParsingContext)
    context = cast(BlockParsingContext, mock_obj)
    context.result_blocks = []
    context.parent_stack = []
    context.is_inside_parent_context = Mock(return_value=False)
    return context
