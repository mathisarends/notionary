from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.schemas import Block


@dataclass
class BlockRenderingContext:
    """Context for processing blocks during markdown conversion."""

    block: Block
    indent_level: int
    block_registry: BlockRegistry
    convert_children_callback: Callable[[list[Block], int], str] | None = None

    # For batch processing
    all_blocks: list[Block] | None = None
    current_block_index: int | None = None
    blocks_consumed: int = 0

    # Result
    markdown_result: str | None = None
    children_result: str | None = None
    was_processed: bool = False

    def has_children(self) -> bool:
        """Check if block has children that need processing."""
        return self.block.has_children and self.block.children is not None and len(self.block.children) > 0

    def get_children_blocks(self) -> list[Block]:
        """Get the children blocks safely."""
        if self.has_children():
            return self.block.children
        return []

    def convert_children_to_markdown(self, indent_level: int = 0) -> str:
        """Convert children blocks to markdown using the callback."""
        if not self.has_children() or not self.convert_children_callback:
            return ""

        return self.convert_children_callback(self.get_children_blocks(), indent_level)
