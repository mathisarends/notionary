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

    def extend(self, other: PositionedBlockList) -> None:
        """Extend this list with another PositionedBlockList."""
        self._blocks.extend(other._blocks)

    def sort_by_position(self) -> None:
        """Sort the blocks by their start position."""
        self._blocks.sort(key=lambda b: b.start_pos)

    def extract_blocks(self) -> list[BlockCreateRequest]:
        """Extract only the blocks from the list."""
        return [pb.block for pb in self._blocks]

    def get_excluded_ranges(self) -> set[int]:
        """Create a set of excluded ranges (character positions) covered by the blocks."""
        excluded = set()
        for block in self._blocks:
            excluded.update(range(block.start_pos, block.end_pos + 1))
        return excluded

    def __len__(self) -> int:
        return len(self._blocks)
