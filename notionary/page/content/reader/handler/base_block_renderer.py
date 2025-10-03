from __future__ import annotations

from abc import ABC, abstractmethod

from notionary.page.content.reader.handler.block_rendering_context import BlockRenderingContext


class BlockHandler(ABC):
    def __init__(self):
        self._next_handler: BlockHandler | None = None

    def set_next(self, handler: BlockHandler) -> BlockHandler:
        self._next_handler = handler
        return handler

    async def handle(self, context: BlockRenderingContext) -> None:
        if self._can_handle(context):
            await self._process(context)
        elif self._next_handler:
            await self._next_handler.handle(context)

    @abstractmethod
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        pass

    @abstractmethod
    async def _process(self, context: BlockRenderingContext) -> None:
        pass

    def _indent_text(self, text: str, spaces: int = 4) -> str:
        if not text:
            return text

        indent = " " * spaces
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
