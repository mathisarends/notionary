from typing import override

from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import Block, BlockType, HeadingData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class HeadingRenderer(BlockRenderer):
    MIN_HEADING_LEVEL = 1
    MAX_HEADING_LEVEL = 3

    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._syntax = self._syntax_registry.get_heading_syntax()
        self._rich_text_markdown_converter = (
            rich_text_markdown_converter or RichTextToMarkdownConverter()
        )

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type in (
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        )

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        level = self._get_heading_level(context.block)
        title = await self._get_heading_title(context.block)

        if not self._is_valid_heading(level, title):
            return

        heading_markdown = self._format_heading(level, title, context.indent_level)

        if self._is_toggleable(context.block):
            context.markdown_result = await self._render_toggleable_heading(
                heading_markdown, context
            )
        else:
            context.markdown_result = heading_markdown

    def _is_valid_heading(self, level: int, title: str) -> bool:
        return self.MIN_HEADING_LEVEL <= level <= self.MAX_HEADING_LEVEL and bool(title)

    def _format_heading(self, level: int, title: str, indent_level: int) -> str:
        heading_prefix = self._syntax.start_delimiter * level
        heading_markdown = f"{heading_prefix} {title}"

        if indent_level > 0:
            indent = "    " * indent_level
            heading_markdown = f"{indent}{heading_markdown}"

        return heading_markdown

    async def _render_toggleable_heading(
        self, heading_markdown: str, context: MarkdownRenderingContext
    ) -> str:
        original_indent = context.indent_level
        context.indent_level += 1

        children_markdown = await context.render_children()

        context.indent_level = original_indent

        if children_markdown:
            return f"{heading_markdown}\n{children_markdown}"
        return heading_markdown

    def _get_heading_level(self, block: Block) -> int:
        if block.type == BlockType.HEADING_1:
            return 1
        elif block.type == BlockType.HEADING_2:
            return 2
        elif block.type == BlockType.HEADING_3:
            return 3
        return 0

    def _is_toggleable(self, block: Block) -> bool:
        heading_data = self._get_heading_data(block)
        return heading_data.is_toggleable if heading_data else False

    async def _get_heading_title(self, block: Block) -> str:
        heading_data = self._get_heading_data(block)

        if not heading_data or not heading_data.rich_text:
            return ""

        return await self._rich_text_markdown_converter.to_markdown(
            heading_data.rich_text
        )

    def _get_heading_data(self, block: Block) -> HeadingData | None:
        if block.type == BlockType.HEADING_1:
            return block.heading_1
        elif block.type == BlockType.HEADING_2:
            return block.heading_2
        elif block.type == BlockType.HEADING_3:
            return block.heading_3
        return None
