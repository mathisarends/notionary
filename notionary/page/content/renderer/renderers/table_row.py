from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import BlockRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class TableRowHandler(BlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.TABLE_ROW

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        """Table rows are internally handled by table as the structure supports it"""
        pass
