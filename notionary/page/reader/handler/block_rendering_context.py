from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from notionary.blocks.models import Block
from notionary.blocks.registry.block_registry import BlockRegistry


@dataclass
class BlockRenderingContext:
    """Context for processing blocks during markdown conversion."""

    block: Block
    indent_level: int
    block_registry: BlockRegistry
    convert_children_callback: Optional[Callable[[list[Block], int], str]] = None

    # For batch processing
    all_blocks: Optional[list[Block]] = None
    current_block_index: Optional[int] = None
    blocks_consumed: int = 0

    # Result
    markdown_result: Optional[str] = None
    children_result: Optional[str] = None
    was_processed: bool = False

    def has_children(self) -> bool:
        """Check if block has children that need processing."""
        return (
            self.block.has_children
            and self.block.children is not None
            and len(self.block.children) > 0
        )

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
