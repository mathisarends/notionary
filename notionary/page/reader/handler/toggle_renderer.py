from notionary.blocks.toggle.toggle_element import ToggleElement
from notionary.page.reader.handler import BlockHandler, BlockRenderingContext


class ToggleRenderer(BlockHandler):
    """Handles toggle blocks with their children content."""

    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return ToggleElement.match_notion(context.block)

    async def _process(self, context: BlockRenderingContext) -> None:
        # Get the toggle title from the block
        toggle_title = self._extract_toggle_title(context.block)

        if not toggle_title:
            return

        # Create toggle start line
        toggle_start = f"+++ {toggle_title}"

        # Apply indentation if needed
        if context.indent_level > 0:
            toggle_start = self._indent_text(
                toggle_start, spaces=context.indent_level * 4
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
                indent_level=0,  # No indentation for content inside toggles
            )

        # Create toggle end line
        toggle_end = "+++"
        if context.indent_level > 0:
            toggle_end = self._indent_text(toggle_end, spaces=context.indent_level * 4)

        # Combine toggle with children content
        if children_markdown:
            context.markdown_result = (
                f"{toggle_start}\n{children_markdown}\n{toggle_end}"
            )
        else:
            context.markdown_result = f"{toggle_start}\n{toggle_end}"

        context.was_processed = True

    def _extract_toggle_title(self, block) -> str:
        """Extract toggle title from the block."""
        if not block.toggle or not block.toggle.rich_text:
            return ""

        title = ""
        for text_obj in block.toggle.rich_text:
            if hasattr(text_obj, "plain_text"):
                title += text_obj.plain_text or ""
            elif hasattr(text_obj, "text") and hasattr(text_obj.text, "content"):
                title += text_obj.text.content or ""

        return title.strip()
