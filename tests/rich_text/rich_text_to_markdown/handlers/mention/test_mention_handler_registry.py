from unittest.mock import Mock

import pytest

from notionary.rich_text.rich_text_to_markdown.handlers.mention.registry import (
    MentionHandlerRegistry,
)
from notionary.rich_text.schemas import MentionType


@pytest.fixture
def registry() -> MentionHandlerRegistry:
    return MentionHandlerRegistry()


@pytest.fixture
def mock_handler() -> Mock:
    return Mock()


def test_register_handler(registry: MentionHandlerRegistry, mock_handler: Mock) -> None:
    registry.register(MentionType.USER, mock_handler)
    result = registry.get_handler(MentionType.USER)
    assert result == mock_handler


def test_get_handler_not_registered(registry: MentionHandlerRegistry) -> None:
    result = registry.get_handler(MentionType.USER)
    assert result is None


def test_register_multiple_handlers(registry: MentionHandlerRegistry) -> None:
    user_handler = Mock()
    page_handler = Mock()
    registry.register(MentionType.USER, user_handler)
    registry.register(MentionType.PAGE, page_handler)
    assert registry.get_handler(MentionType.USER) == user_handler
    assert registry.get_handler(MentionType.PAGE) == page_handler


def test_register_overwrites_existing_handler(registry: MentionHandlerRegistry) -> None:
    old_handler = Mock()
    new_handler = Mock()
    registry.register(MentionType.USER, old_handler)
    registry.register(MentionType.USER, new_handler)
    result = registry.get_handler(MentionType.USER)
    assert result == new_handler
    assert result != old_handler
