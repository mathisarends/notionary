from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.syntax.definition import (
    MarkdownGrammar,
    SyntaxDefinitionRegistry,
)
from notionary.rich_text.markdown_to_rich_text.service import (
    MarkdownRichTextConverter,
)


@pytest.fixture
def syntax_registry() -> SyntaxDefinitionRegistry:
    return SyntaxDefinitionRegistry()


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def mock_rich_text_converter() -> MarkdownRichTextConverter:
    mock_obj = AsyncMock(spec=MarkdownRichTextConverter)
    converter = cast(MarkdownRichTextConverter, mock_obj)
    converter.to_rich_text = AsyncMock(
        return_value=[{"type": "text", "text": {"content": "test"}}]
    )
    return converter


@pytest.fixture
def context() -> BlockParsingContext:
    mock_obj = Mock(spec=BlockParsingContext)
    context = cast(BlockParsingContext, mock_obj)
    context.result_blocks = []
    context.parent_stack = []
    context.is_inside_parent_context = Mock(return_value=False)
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])
    context.strip_indentation_level = Mock(return_value=[])
    context.parse_nested_markdown = AsyncMock(return_value=[])
    context.get_remaining_lines = Mock(return_value=[])
    context.lines_consumed = 0
    return context
