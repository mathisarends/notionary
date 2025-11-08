from __future__ import annotations

from abc import ABC, abstractmethod

from notionary.blocks.schemas import Block
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.renderer.context import MarkdownRenderingContext


class BlockRenderer(ABC):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        self._syntax_registry = syntax_registry
        self._next_handler: BlockRenderer | None = None

    def set_next(self, handler: BlockRenderer) -> BlockRenderer:
        self._next_handler = handler
        return handler

    async def handle(self, context: MarkdownRenderingContext) -> None:
        if self._can_handle(context.block):
            await self._process(context)
        elif self._next_handler:
            await self._next_handler.handle(context)

    @abstractmethod
    def _can_handle(self, block: Block) -> bool:
        pass

    @abstractmethod
    async def _process(self, context: MarkdownRenderingContext) -> None:
        pass
