from unittest.mock import Mock

import pytest

from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.registry import (
    RichTextHandlerRegistry,
)
from notionary.rich_text.schemas import RichTextType


@pytest.fixture
def registry() -> RichTextHandlerRegistry:
    return RichTextHandlerRegistry()


@pytest.fixture
def mock_handler() -> Mock:
    return Mock()


def test_register_handler(
    registry: RichTextHandlerRegistry, mock_handler: Mock
) -> None:
    registry.register(RichTextType.TEXT, mock_handler)
    result = registry.get_handler(RichTextType.TEXT)
    assert result == mock_handler


def test_get_handler_not_registered(registry: RichTextHandlerRegistry) -> None:
    result = registry.get_handler(RichTextType.TEXT)
    assert result is None


def test_register_multiple_handlers(registry: RichTextHandlerRegistry) -> None:
    text_handler = Mock()
    mention_handler = Mock()
    registry.register(RichTextType.TEXT, text_handler)
    registry.register(RichTextType.MENTION, mention_handler)
    assert registry.get_handler(RichTextType.TEXT) == text_handler
    assert registry.get_handler(RichTextType.MENTION) == mention_handler


def test_register_overwrites_existing_handler(
    registry: RichTextHandlerRegistry,
) -> None:
    old_handler = Mock()
    new_handler = Mock()
    registry.register(RichTextType.TEXT, old_handler)
    registry.register(RichTextType.TEXT, new_handler)
    result = registry.get_handler(RichTextType.TEXT)
    assert result == new_handler
    assert result != old_handler
