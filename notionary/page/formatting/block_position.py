from dataclasses import dataclass
from notionary.blocks.block_models import BlockCreateRequest


@dataclass
class PositionedBlock:
    """Ein Block mit seiner Position im Text."""

    start_pos: int
    end_pos: int
    block: BlockCreateRequest


class PositionedBlockList:
    """Liste von PositionedBlocks mit den minimal nötigen Operationen."""

    def __init__(self):
        self._blocks: list[PositionedBlock] = []

    def add(self, start_pos: int, end_pos: int, block: BlockCreateRequest) -> None:
        """Fügt einen Block hinzu."""
        self._blocks.append(PositionedBlock(start_pos, end_pos, block))

    def extend_from_tuples(
        self, tuples: list[tuple[int, int, BlockCreateRequest]]
    ) -> None:
        """Fügt Blöcke aus Tupel-Liste hinzu."""
        for start_pos, end_pos, block in tuples:
            self.add(start_pos, end_pos, block)

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
