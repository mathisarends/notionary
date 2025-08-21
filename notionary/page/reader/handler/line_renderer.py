from notionary.page.reader.handler import BlockHandler, BlockRenderingContext


class LineRenderer(BlockHandler):
    """Handles all regular blocks that don't need special parent/children processing."""

    def _can_handle(self, context: BlockRenderingContext) -> bool:
        # Always can handle - this is the fallback handler
        return True

    def _process(self, context: BlockRenderingContext) -> None:
        # Convert the block itself
        block_markdown = context.block_registry.notion_to_markdown(context.block)

        # If block has no direct markdown, either return empty or process children
        if not block_markdown:
            if not context.has_children():
                context.markdown_result = ""
                context.was_processed = True
                return

            # Import here to avoid circular dependency and process children
            from notionary.page.reader.page_content_retriever import \
                PageContentRetriever

            retriever = PageContentRetriever(context.block_registry)
            children_markdown = retriever._convert_blocks_to_markdown(
                context.get_children_blocks(), indent_level=context.indent_level + 1
            )
            context.markdown_result = children_markdown
            context.was_processed = True
            return

        # Apply indentation if needed
        if context.indent_level > 0:
            block_markdown = self._indent_text(
                block_markdown, spaces=context.indent_level * 4
            )

        # If there are no children, return the block markdown directly
        if not context.has_children():
            context.markdown_result = block_markdown
            context.was_processed = True
            return

        # Otherwise process children and combine
        from notionary.page.reader.page_content_retriever import \
            PageContentRetriever

        retriever = PageContentRetriever(context.block_registry)
        children_markdown = retriever._convert_blocks_to_markdown(
            context.get_children_blocks(), indent_level=context.indent_level + 1
        )

        context.markdown_result = (
            f"{block_markdown}\n{children_markdown}"
            if children_markdown
            else block_markdown
        )
        context.was_processed = True
