from __future__ import annotations

from dataclasses import dataclass, field

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.registry.block_registry import BlockRegistry


@dataclass
class ParentBlockContext:
    """Context for a block that expects children."""

    block: BlockCreateRequest
    element_type: BaseBlockElement
    child_lines: list[str]
    child_blocks: list[BlockCreateRequest] = field(default_factory=list)

    def add_child_line(self, content: str):
        """Adds a child line."""
        self.child_lines.append(content)

    def add_child_block(self, block: BlockCreateRequest):
        """Adds a processed child block."""
        self.child_blocks.append(block)

    def has_children(self) -> bool:
        """Checks if children have been collected."""
        return len(self.child_lines) > 0 or len(self.child_blocks) > 0


@dataclass
class LineProcessingContext:
    """Context that gets passed through the handler chain."""

    line: str
    result_blocks: list[BlockCreateRequest]
    parent_stack: list[ParentBlockContext]
    block_registry: BlockRegistry

    all_lines: list[str] | None = None
    current_line_index: int | None = None
    lines_consumed: int = 0

    # Result indicators
    was_processed: bool = False
    should_continue: bool = False

    def get_remaining_lines(self) -> list[str]:
        """Get all remaining lines from current position."""
        if self.all_lines is None or self.current_line_index is None:
            return []
        return self.all_lines[self.current_line_index + 1 :]
