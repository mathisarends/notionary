from notionary.blocks.mappings.toggle import ToggleMapper
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer
from notionary.page.content.reader.handler.utils import indent_text


class ToggleRenderer(BlockRenderer):
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return ToggleMapper.match_notion(context.block)

    async def _process(self, context: BlockRenderingContext) -> None:
        # Get the toggle title from the block
        toggle_title = self._extract_toggle_title(context.block)

        if not toggle_title:
            return

        # Create toggle start line
        toggle_start = f"+++ {toggle_title}"

        # Apply indentation if needed
        if context.indent_level > 0:
            toggle_start = indent_text(toggle_start, spaces=context.indent_level * 4)

        # Process children if they exist
        children_markdown = ""
        if context.has_children():
            # Import here to avoid circular dependency
            from notionary.page.content.reader.service import (
                NotionToMarkdownConverter,
            )

            # Create a temporary retriever to process children
            retriever = NotionToMarkdownConverter(context.block_registry)
            children_markdown = await retriever.convert(
                context.get_children_blocks(),
                indent_level=0,  # No indentation for content inside toggles
            )

        # Create toggle end line
        toggle_end = "+++"
        if context.indent_level > 0:
            toggle_end = indent_text(toggle_end, spaces=context.indent_level * 4)

        # Combine toggle with children content
        if children_markdown:
            context.markdown_result = f"{toggle_start}\n{children_markdown}\n{toggle_end}"
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
