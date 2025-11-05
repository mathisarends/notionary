from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.port import (
    RichTextHandler,
)
from notionary.rich_text.schemas import RichTextType


class RichTextHandlerRegistry:
    def __init__(self):
        self._handlers: dict[RichTextType, RichTextHandler] = {}

    def register(self, rich_text_type: RichTextType, handler: RichTextHandler) -> None:
        self._handlers[rich_text_type] = handler

    def get_handler(self, rich_text_type: RichTextType) -> RichTextHandler | None:
        return self._handlers.get(rich_text_type)
