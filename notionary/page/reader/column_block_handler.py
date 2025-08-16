from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.column.column_list_element import ColumnListElement
from notionary.page.reader.block_handler import BlockHandler
from notionary.page.reader.context import BlockProcessingContext


class ColumnBlockHandler(BlockHandler):
    """Handles column and column list blocks with their children content."""

    def _can_handle(self, context: BlockProcessingContext) -> bool:
        return (
            ColumnElement.match_notion(context.block) or 
            ColumnListElement.match_notion(context.block)
        )

    def _process(self, context: BlockProcessingContext) -> None:
        # Convert the column block itself
        column_markdown = context.block_registry.notion_to_markdown(context.block)
        
        if not column_markdown:
            return
            
        # Apply indentation if needed
        if context.indent_level > 0:
            column_markdown = self._indent_text(
                column_markdown, spaces=context.indent_level * 4
            )
        
        # Process children if they exist
        children_markdown = ""
        if context.has_children():
            # Import here to avoid circular dependency
            from notionary.page.reader.block_processor import BlockProcessor
            
            processor = BlockProcessor(context.block_registry)
            children_markdown = processor.convert_blocks_to_markdown(
                context.get_children_blocks(), 
                indent_level=context.indent_level + 1
            )
        
        # Combine column with children content
        if children_markdown:
            context.markdown_result = f"{column_markdown}\n{children_markdown}"
        else:
            context.markdown_result = column_markdown
            
        context.was_processed = True
