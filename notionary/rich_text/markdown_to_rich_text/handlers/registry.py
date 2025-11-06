import re
from re import Match

from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.markdown_to_rich_text.models import PatternMatch
from notionary.rich_text.schemas import RichText


class PatternHandlerRegistry:
    def __init__(self, handlers: list[BasePatternHandler]) -> None:
        self._handlers = handlers

    def find_earliest_match(self, text: str) -> PatternMatch | None:
        earliest_match = None
        earliest_position = len(text)

        for handler in self._handlers:
            match = re.search(handler.pattern, text)
            if match and match.start() < earliest_position:
                earliest_match = PatternMatch(
                    match=match,
                    handler=self._create_handler_callable(handler),
                    position=match.start(),
                )
                earliest_position = match.start()

        return earliest_match

    async def process_match(
        self, pattern_match: PatternMatch
    ) -> RichText | list[RichText]:
        handler_callable = pattern_match.handler
        return await handler_callable(pattern_match.match)

    def _create_handler_callable(self, handler: BasePatternHandler):
        async def wrapper(match: Match) -> RichText | list[RichText]:
            return await handler.handle(match)

        return wrapper
