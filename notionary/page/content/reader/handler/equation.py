from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class EquationRenderer(BlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.EQUATION

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        expression = self._extract_equation_expression(context.block)

        if not expression:
            context.markdown_result = ""
            return

        equation_markdown = f"$${expression}$$"

        if context.indent_level > 0:
            equation_markdown = context.indent_text(equation_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{equation_markdown}\n{children_markdown}"
        else:
            context.markdown_result = equation_markdown

    def _extract_equation_expression(self, block: Block) -> str:
        if not block.equation:
            return ""
        return block.equation.expression or ""
