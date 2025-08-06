from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.registry.block_registry import BlockRegistry

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateRequest


@dataclass
class ParentBlockContext:
    """Context for a block that expects children."""

    block: BlockCreateRequest
    element_type: NotionBlockElement
    child_prefix: str
    child_lines: list[str]

    def add_child_line(self, content: str):
        """Adds a child line."""
        self.child_lines.append(content)

    def has_children(self) -> bool:
        """Checks if children have been collected."""
        return len(self.child_lines) > 0


@dataclass
class LineProcessingContext:
    """Context that gets passed through the handler chain."""

    line: str
    result_blocks: list[BlockCreateRequest]
    parent_stack: list[ParentBlockContext]
    block_registry: BlockRegistry

    # Result indicators
    was_processed: bool = False
    should_continue: bool = False


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