from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class TableOfContentsRenderer(BlockRenderer):
    TABLE_OF_CONTENTS_MARKDOWN = "[[TOC]]"

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.TABLE_OF_CONTENTS

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        toc_markdown = self.TABLE_OF_CONTENTS_MARKDOWN

        if context.indent_level > 0:
            toc_markdown = context.indent_text(toc_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{toc_markdown}\n{children_markdown}"
        else:
            context.markdown_result = toc_markdown
