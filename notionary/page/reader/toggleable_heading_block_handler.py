from notionary.blocks.toggleable_heading.toggleable_heading_element import ToggleableHeadingElement
from notionary.blocks.block_types import BlockType
from notionary.page.reader.block_handler import BlockHandler
from notionary.page.reader.context import BlockProcessingContext


class ToggleableHeadingBlockHandler(BlockHandler):
    """Handles toggleable heading blocks with their children content."""

    def _can_handle(self, context: BlockProcessingContext) -> bool:
        return ToggleableHeadingElement.match_notion(context.block)

    def _process(self, context: BlockProcessingContext) -> None:
        # Get the heading level and title
        level, title = self._extract_heading_info(context.block)
        
        if not title or level == 0:
            return
            
        # Create toggleable heading start line
        prefix = "+++" + ("#" * level)
        heading_start = f"{prefix} {title}"
        
        # Apply indentation if needed
        if context.indent_level > 0:
            heading_start = self._indent_text(
                heading_start, spaces=context.indent_level * 4
            )
        
        # Process children if they exist
        children_markdown = ""
        if context.has_children():
            # Import here to avoid circular dependency
            from notionary.page.reader.block_processor import BlockProcessor
            
            processor = BlockProcessor(context.block_registry)
            children_markdown = processor.convert_blocks_to_markdown(
                context.get_children_blocks(), 
                indent_level=0  # No indentation for content inside toggleable headings
            )
        
        # Create toggleable heading end line
        heading_end = "+++"
        if context.indent_level > 0:
            heading_end = self._indent_text(
                heading_end, spaces=context.indent_level * 4
            )
        
        # Combine heading with children content
        if children_markdown:
            context.markdown_result = f"{heading_start}\n{children_markdown}\n{heading_end}"
        else:
            context.markdown_result = f"{heading_start}\n{heading_end}"
            
        context.was_processed = True

    def _extract_heading_info(self, block) -> tuple[int, str]:
        """Extract heading level and title from the block."""
        # Determine heading level from block type
        if block.type == BlockType.HEADING_1:
            level = 1
            heading_content = block.heading_1
        elif block.type == BlockType.HEADING_2:
            level = 2
            heading_content = block.heading_2
        elif block.type == BlockType.HEADING_3:
            level = 3
            heading_content = block.heading_3
        else:
            return 0, ""
        
        if not heading_content or not heading_content.rich_text:
            return level, ""
        
        # Extract title from rich_text
        title = ""
        for text_obj in heading_content.rich_text:
            if hasattr(text_obj, "plain_text"):
                title += text_obj.plain_text or ""
            elif hasattr(text_obj, "text") and hasattr(text_obj.text, "content"):
                title += text_obj.text.content or ""
        
        return level, title.strip()
