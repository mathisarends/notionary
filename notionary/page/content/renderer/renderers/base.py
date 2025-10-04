from __future__ import annotations

from abc import ABC, abstractmethod

from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import BlockRenderingContext


class BlockRenderer(ABC):
    def __init__(self) -> None:
        self._next_handler: BlockRenderer | None = None

    def set_next(self, handler: BlockRenderer) -> BlockRenderer:
        self._next_handler = handler
        return handler

    async def handle(self, context: BlockRenderingContext) -> None:
        if self._can_handle(context.block):
            await self._process(context)
        elif self._next_handler:
            await self._next_handler.handle(context)

    @abstractmethod
    def _can_handle(self, block: Block) -> bool:
        pass

    @abstractmethod
    async def _process(self, context: BlockRenderingContext) -> None:
        pass
