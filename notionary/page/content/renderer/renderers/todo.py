from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax import SyntaxRegistry


class TodoRenderer(BlockRenderer):
    def __init__(
        self,
        syntax_registry: SyntaxRegistry | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.TO_DO

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        is_checked, content = await self._extract_todo_info(context.block)

        if not content:
            context.markdown_result = ""
            return

        syntax = self._syntax_registry.get_todo_done_syntax() if is_checked else self._syntax_registry.get_todo_syntax()

        todo_markdown = f"{syntax.start_delimiter} {content}"

        if context.indent_level > 0:
            todo_markdown = context.indent_text(todo_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{todo_markdown}\n{children_markdown}"
        else:
            context.markdown_result = todo_markdown

    async def _extract_todo_info(self, block: Block) -> tuple[bool, str]:
        if not block.to_do:
            return False, ""

        is_checked = block.to_do.checked or False

        content = ""
        if block.to_do.rich_text:
            content = await self._rich_text_markdown_converter.to_markdown(block.to_do.rich_text)

        return is_checked, content
