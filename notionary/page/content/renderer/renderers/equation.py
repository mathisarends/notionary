from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class EquationRenderer(BlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.EQUATION

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        expression = self._extract_equation_expression(context.block)

        if not expression:
            context.markdown_result = ""
            return

        syntax = self._syntax_registry.get_equation_syntax()
        equation_markdown = f"{syntax.start_delimiter}{expression}{syntax.end_delimiter}"

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
