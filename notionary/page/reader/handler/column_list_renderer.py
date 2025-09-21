from notionary.blocks.column.column_list_element import ColumnListElement
from notionary.page.reader.handler import BlockHandler, BlockRenderingContext


class ColumnListRenderer(BlockHandler):
    """Handles column list blocks with their column children."""

    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return ColumnListElement.match_notion(context.block)

    async def _process(self, context: BlockRenderingContext) -> None:
        # Create column list start line
        column_list_start = "::: columns"

        # Apply indentation if needed
        if context.indent_level > 0:
            column_list_start = self._indent_text(column_list_start, spaces=context.indent_level * 4)

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
                indent_level=0,  # No indentation for content inside column lists
            )

        # Create column list end line
        column_list_end = ":::"
        if context.indent_level > 0:
            column_list_end = self._indent_text(column_list_end, spaces=context.indent_level * 4)

        # Combine column list with children content
        if children_markdown:
            context.markdown_result = f"{column_list_start}\n{children_markdown}\n{column_list_end}"
        else:
            context.markdown_result = f"{column_list_start}\n{column_list_end}"

        context.was_processed = True
