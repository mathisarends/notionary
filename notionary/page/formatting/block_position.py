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
    """Liste von PositionedBlocks mit minimalen Operationen."""

    def __init__(self):
        self._blocks: list[PositionedBlock] = []

    def add(self, start_pos: int, end_pos: int, block: BlockCreateRequest) -> None:
        """Fügt einen Block hinzu."""
        self._blocks.append(PositionedBlock(start_pos, end_pos, block))

    def extend(self, other: "PositionedBlockList") -> None:
        """Erweitert diese Liste um eine andere."""
        self._blocks.extend(other._blocks)

    def sort_by_position(self) -> None:
        """Sortiert nach Start-Position."""
        self._blocks.sort(key=lambda b: b.start_pos)

    def extract_blocks(self) -> list[BlockCreateRequest]:
        """Extrahiert nur die Blöcke."""
        return [pb.block for pb in self._blocks]

    def get_excluded_ranges(self) -> set[int]:
        """Erstellt excluded ranges Set."""
        excluded = set()
        for block in self._blocks:
            excluded.update(range(block.start_pos, block.end_pos + 1))
        return excluded

    def __len__(self) -> int:
        return len(self._blocks)
