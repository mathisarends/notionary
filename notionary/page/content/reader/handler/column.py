from notionary.blocks.mappings.column import ColumnMapper
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer
from notionary.page.content.reader.handler.utils import indent_text


class ColumnRenderer(BlockRenderer):
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return ColumnMapper.match_notion(context.block)

    async def _process(self, context: BlockRenderingContext) -> None:
        column_start = self._extract_column_start(context.block)

        # Apply indentation if needed
        if context.indent_level > 0:
            column_start = indent_text(column_start, spaces=context.indent_level * 4)

        # Process children if they exist
        children_markdown = ""
        if context.has_children():
            from notionary.page.content.reader.service import (
                NotionToMarkdownConverter,
            )

            # Create a temporary retriever to process children
            retriever = NotionToMarkdownConverter(context.block_registry)
            children_markdown = await retriever.convert(
                context.get_children_blocks(),
                indent_level=0,  # No indentation for content inside columns
            )

        # Create column end line
        column_end = ":::"
        if context.indent_level > 0:
            column_end = indent_text(column_end, spaces=context.indent_level * 4)

        # Combine column with children content
        if children_markdown:
            context.markdown_result = f"{column_start}\n{children_markdown}\n{column_end}"
        else:
            context.markdown_result = f"{column_start}\n{column_end}"

        context.was_processed = True

    def _extract_column_start(self, block) -> str:
        """Extract column start line with potential width ratio."""
        if not block.column:
            return "::: column"

        width_ratio = block.column.width_ratio
        if width_ratio:
            return f"::: column {width_ratio}"
        else:
            return "::: column"
