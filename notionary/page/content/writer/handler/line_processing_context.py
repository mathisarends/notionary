from __future__ import annotations

from dataclasses import dataclass, field

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.schemas import BlockCreatePayload


@dataclass
class ParentBlockContext:
    block: BlockCreatePayload
    element_type: NotionMarkdownMapper
    child_lines: list[str]
    child_blocks: list[BlockCreatePayload] = field(default_factory=list)

    def add_child_line(self, content: str) -> None:
        self.child_lines.append(content)

    def add_child_block(self, block: BlockCreatePayload) -> None:
        self.child_blocks.append(block)

    def has_children(self) -> bool:
        return len(self.child_lines) > 0 or len(self.child_blocks) > 0


@dataclass
class LineProcessingContext:
    line: str
    result_blocks: list[BlockCreatePayload]
    parent_stack: list[ParentBlockContext]
    block_registry: BlockRegistry

    all_lines: list[str] | None = None
    current_line_index: int | None = None
    lines_consumed: int = 0

    # Result indicators
    was_processed: bool = False
    should_continue: bool = False

    def get_remaining_lines(self) -> list[str]:
        if self.all_lines is None or self.current_line_index is None:
            return []
        return self.all_lines[self.current_line_index + 1 :]
