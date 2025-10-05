from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.schemas import BlockCreatePayload


# Gucken ob der hier so umfangreich sein muss wie er es jetzt ist
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


ParseChildrenCallback = Callable[[list[str]], Awaitable[list[BlockCreatePayload]]]


@dataclass
class BlockParsingContext:
    line: str
    result_blocks: list[BlockCreatePayload]
    parent_stack: list[ParentBlockContext]
    block_registry: BlockRegistry

    parse_children_callback: ParseChildrenCallback | None = None

    all_lines: list[str] | None = None
    current_line_index: int | None = None
    lines_consumed: int = 0

    async def parse_nested_content(self, nested_lines: list[str]) -> list[BlockCreatePayload]:
        if not self.parse_children_callback or not nested_lines:
            return []

        return await self.parse_children_callback(nested_lines)

    def get_remaining_lines(self) -> list[str]:
        if self.all_lines is None or self.current_line_index is None:
            return []
        return self.all_lines[self.current_line_index + 1 :]

    def is_inside_parent_context(self) -> bool:
        return len(self.parent_stack) > 0
