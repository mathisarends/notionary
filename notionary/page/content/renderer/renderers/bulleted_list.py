from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.rich_text_to_markdown.service import (
    RichTextToMarkdownConverter,
)


class BulletedListRenderer(BlockRenderer):
    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._rich_text_markdown_converter = (
            rich_text_markdown_converter or RichTextToMarkdownConverter()
        )

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.BULLETED_LIST_ITEM

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        markdown = await self._convert_bulleted_list_to_markdown(context.block)

        if not markdown:
            context.markdown_result = ""
            return

        syntax = self._syntax_registry.get_bulleted_list_syntax()
        list_item_markdown = f"{syntax.start_delimiter}{markdown}"

        if context.indent_level > 0:
            list_item_markdown = context.indent_text(list_item_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{list_item_markdown}\n{children_markdown}"
        else:
            context.markdown_result = list_item_markdown

    async def _convert_bulleted_list_to_markdown(self, block: Block) -> str | None:
        if not block.bulleted_list_item or not block.bulleted_list_item.rich_text:
            return None

        return await self._rich_text_markdown_converter.to_markdown(
            block.bulleted_list_item.rich_text
        )
