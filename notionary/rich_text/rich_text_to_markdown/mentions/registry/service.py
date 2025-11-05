from notionary.rich_text.rich_text_to_markdown.mentions.port import MentionHandler
from notionary.rich_text.schemas import MentionType


class MentionHandlerRegistry:
    def __init__(self):
        self._handlers: dict[MentionType, MentionHandler] = {}

    def register(self, mention_type: MentionType, handler: MentionHandler) -> None:
        self._handlers[mention_type] = handler

    def get_handler(self, mention_type: MentionType) -> MentionHandler | None:
        return self._handlers.get(mention_type)
