from notionary.page.reader.block_handler import BlockHandler
from notionary.page.reader.context import BlockProcessingContext


class RegularBlockHandler(BlockHandler):
    """Handles all regular blocks that don't need special parent/children processing."""

    def _can_handle(self, context: BlockProcessingContext) -> bool:
        # Always can handle - this is the fallback handler
        return True

    def _process(self, context: BlockProcessingContext) -> None:
        # Convert the block itself
        block_markdown = context.block_registry.notion_to_markdown(context.block)
        
        if not block_markdown:
            # If no content but has children, process children
            if context.has_children():
                from notionary.page.reader.block_processor import BlockProcessor
                
                processor = BlockProcessor(context.block_registry)
                children_markdown = processor.convert_blocks_to_markdown(
                    context.get_children_blocks(), 
                    indent_level=context.indent_level + 1
                )
                context.markdown_result = children_markdown
            else:
                context.markdown_result = ""
            context.was_processed = True
            return
            
        # Apply indentation if needed
        if context.indent_level > 0:
            block_markdown = self._indent_text(
                block_markdown, spaces=context.indent_level * 4
            )
        
        # Process children if they exist
        children_markdown = ""
        if context.has_children():
            from notionary.page.reader.block_processor import BlockProcessor
            
            processor = BlockProcessor(context.block_registry)
            children_markdown = processor.convert_blocks_to_markdown(
                context.get_children_blocks(), 
                indent_level=context.indent_level + 1
            )
        
        # Combine block with children content
        if children_markdown:
            context.markdown_result = f"{block_markdown}\n{children_markdown}"
        else:
            context.markdown_result = block_markdown
            
        context.was_processed = True
