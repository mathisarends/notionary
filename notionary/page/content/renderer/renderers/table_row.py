from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class TableRowHandler(BlockRenderer):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry=syntax_registry)

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.TABLE_ROW

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        """Table rows are internally handled by table as the structure supports it (direct table childs are always table rows)"""
        pass
