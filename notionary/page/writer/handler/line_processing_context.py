from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.block_models import BlockCreateRequest


@dataclass
class ParentBlockContext:
    """Context for a block that expects children."""

    block: BlockCreateRequest
    element_type: NotionBlockElement
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

    all_lines: Optional[list[str]] = None
    current_line_index: Optional[int] = None
    lines_consumed: int = 0

    # Result indicators
    was_processed: bool = False
    should_continue: bool = False

    def get_remaining_lines(self) -> list[str]:
        """Get all remaining lines from current position."""
        if self.all_lines is None or self.current_line_index is None:
            return []
        return self.all_lines[self.current_line_index + 1 :]
