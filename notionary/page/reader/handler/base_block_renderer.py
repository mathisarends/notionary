from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from notionary.page.reader.handler.block_rendering_context import BlockRenderingContext


class BlockHandler(ABC):
    """Abstract base class for block handlers."""

    def __init__(self):
        self._next_handler: Optional[BlockHandler] = None

    def set_next(self, handler: BlockHandler) -> BlockHandler:
        """Set the next handler in the chain."""
        self._next_handler = handler
        return handler

    def handle(self, context: BlockRenderingContext) -> None:
        """Handle the block or pass to next handler."""
        if self._can_handle(context):
            self._process(context)
        elif self._next_handler:
            self._next_handler.handle(context)

    @abstractmethod
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        """Check if this handler can process the current block."""
        pass

    @abstractmethod
    def _process(self, context: BlockRenderingContext) -> None:
        """Process the block and update context."""
        pass

    def _indent_text(self, text: str, spaces: int = 4) -> str:
        """Indent each line of text with specified number of spaces."""
        if not text:
            return text

        indent = " " * spaces
        lines = text.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
