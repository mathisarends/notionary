from notionary.blocks.column.column_element import ColumnElement
from notionary.page.reader.handler import BlockHandler, BlockRenderingContext


class ColumnRenderer(BlockHandler):
    """Handles individual column blocks with their children content."""

    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return ColumnElement.match_notion(context.block)

    async def _process(self, context: BlockRenderingContext) -> None:
        # Get the column start line with potential width ratio
        column_start = self._extract_column_start(context.block)

        # Apply indentation if needed
        if context.indent_level > 0:
            column_start = self._indent_text(
                column_start, spaces=context.indent_level * 4
            )

        # Process children if they exist
        children_markdown = ""
        if context.has_children():
            # Import here to avoid circular dependency
            from notionary.page.reader.page_content_retriever import (
                PageContentRetriever,
            )

            # Create a temporary retriever to process children
            retriever = PageContentRetriever(context.block_registry)
            children_markdown = await retriever._convert_blocks_to_markdown(
                context.get_children_blocks(),
                indent_level=0,  # No indentation for content inside columns
            )

        # Create column end line
        column_end = ":::"
        if context.indent_level > 0:
            column_end = self._indent_text(column_end, spaces=context.indent_level * 4)

        # Combine column with children content
        if children_markdown:
            context.markdown_result = (
                f"{column_start}\n{children_markdown}\n{column_end}"
            )
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
