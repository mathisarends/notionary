from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from notionary.page.writer.handler.line_processing_context import \
    LineProcessingContext


class LineHandler(ABC):
    """Abstract base class for line handlers."""

    def __init__(self):
        self._next_handler: Optional[LineHandler] = None

    def set_next(self, handler: LineHandler) -> LineHandler:
        """Set the next handler in the chain."""
        self._next_handler = handler
        return handler

    def handle(self, context: LineProcessingContext) -> None:
        """Handle the line or pass to next handler."""
        if self._can_handle(context):
            self._process(context)
        elif self._next_handler:
            self._next_handler.handle(context)

    @abstractmethod
    def _can_handle(self, context: LineProcessingContext) -> bool:
        """Check if this handler can process the current line."""
        pass

    @abstractmethod
    def _process(self, context: LineProcessingContext) -> None:
        """Process the line and update context."""
        pass
