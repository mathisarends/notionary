from __future__ import annotations

from abc import ABC, abstractmethod

from notionary.page.content.parser.context import BlockParsingContext


class LineParser(ABC):
    def __init__(self) -> None:
        self._next_handler: LineParser | None = None

    def set_next(self, handler: LineParser) -> LineParser:
        self._next_handler = handler
        return handler

    async def handle(self, context: BlockParsingContext) -> None:
        if self._can_handle(context):
            await self._process(context)
        elif self._next_handler:
            await self._next_handler.handle(context)

    @abstractmethod
    def _can_handle(self, context: BlockParsingContext) -> bool:
        pass

    @abstractmethod
    async def _process(self, context: BlockParsingContext) -> None:
        pass
