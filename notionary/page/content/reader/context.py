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

    # markdown indentation
    indent_space_multiplier = 4

    async def render_children(self) -> str:
        return await self._convert_children_to_markdown(self.indent_level)

    async def render_children_with_additional_indent(self, additional_indent: int) -> str:
        return await self._convert_children_to_markdown(self.indent_level + additional_indent)

    async def _convert_children_to_markdown(self, indent_level: int) -> str:
        if not self.has_children() or not self.convert_children_callback:
            return ""

        return await self.convert_children_callback(self.get_children_blocks(), indent_level)

    def has_children(self) -> bool:
        return self.block.has_children and self.block.children is not None and len(self.block.children) > 0

    def get_children_blocks(self) -> list[Block]:
        if self.has_children():
            return self.block.children
        return []

    def indent_text(self, text: str) -> str:
        if not text:
            return text

        spaces = " " * self.indent_space_multiplier * self.indent_level
        lines = text.split("\n")
        return "\n".join(f"{spaces}{line}" if line.strip() else line for line in lines)
