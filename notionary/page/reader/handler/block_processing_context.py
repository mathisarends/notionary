from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from notionary.blocks.models import Block
from notionary.blocks.registry.block_registry import BlockRegistry


@dataclass
class BlockProcessingContext:
    """Context for processing blocks during markdown conversion."""

    block: Block
    indent_level: int
    block_registry: BlockRegistry

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
