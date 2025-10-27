from typing import override

from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax.definition import (
    MarkdownGrammar,
    SyntaxDefinitionRegistry,
)


class NumberedListRenderer(BlockRenderer):
    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
        markdown_grammar: MarkdownGrammar | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._rich_text_markdown_converter = (
            rich_text_markdown_converter or RichTextToMarkdownConverter()
        )

        markdown_grammar = markdown_grammar or MarkdownGrammar()
        self._numbered_list_placeholder = markdown_grammar.numbered_list_placeholder

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.NUMBERED_LIST_ITEM

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        list_item_data = context.block.numbered_list_item
        rich_text = list_item_data.rich_text if list_item_data else []
        content = await self._rich_text_markdown_converter.to_markdown(rich_text)

        item_line = context.indent_text(f"{self._numbered_list_placeholder}. {content}")

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{item_line}\n{children_markdown}"
        else:
            context.markdown_result = item_line
