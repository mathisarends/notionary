from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateRequest


@dataclass
class PositionedBlock:
    """A block with its position in the text."""

    start_pos: int
    end_pos: int
    block: BlockCreateRequest


class PositionedBlockList:
    """List of PositionedBlocks with minimal operations."""

    def __init__(self):
        self._blocks: list[PositionedBlock] = []

    def add(self, start_pos: int, end_pos: int, block: BlockCreateRequest) -> None:
        """Add a block to the list."""
        self._blocks.append(PositionedBlock(start_pos, end_pos, block))

    def extract_blocks(self) -> list[BlockCreateRequest]:
        """Extract only the blocks from the list."""
        return [pb.block for pb in self._blocks]

    def __len__(self) -> int:
        return len(self._blocks)
