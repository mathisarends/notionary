from collections.abc import Callable
from dataclasses import dataclass

from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.schemas import Block


@dataclass
class BlockRenderingContext:
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
    was_processed: bool = False

    def has_children(self) -> bool:
        return self.block.has_children and self.block.children is not None and len(self.block.children) > 0

    def get_children_blocks(self) -> list[Block]:
        if self.has_children():
            return self.block.children
        return []
