from typing import override

from notionary.page.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.markdown.syntax.definition import SyntaxDefinitionRegistry


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
