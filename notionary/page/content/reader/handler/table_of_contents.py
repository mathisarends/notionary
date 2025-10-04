from typing import override

from notionary.blocks.schemas import BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class TableOfContentsRenderer(BlockRenderer):
    TABLE_OF_CONTENTS_MARKDOWN = "[[TOC]]"

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.TABLE_OF_CONTENTS

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        toc_markdown = self.TABLE_OF_CONTENTS_MARKDOWN

        if context.indent_level > 0:
            toc_markdown = context.indent_text(toc_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{toc_markdown}\n{children_markdown}"
        else:
            context.markdown_result = toc_markdown

        context.was_processed = True
