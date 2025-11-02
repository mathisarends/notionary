from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.post_processing.service import (
    MarkdownRenderingPostProcessor,
)
from notionary.page.content.renderer.renderers import BlockRenderer
from notionary.utils.decorators import time_execution_async
from notionary.utils.mixins.logging import LoggingMixin


class NotionToMarkdownConverter(LoggingMixin):
    def __init__(
        self,
        renderer_chain: BlockRenderer,
        post_processor: MarkdownRenderingPostProcessor,
    ) -> None:
        self._renderer_chain = renderer_chain
        self._post_processor = post_processor

    @time_execution_async()
    async def convert(self, blocks: list[Block], indent_level: int = 0) -> str:
        if not blocks:
            return ""

        rendered_block_parts = []
        current_block_index = 0

        while current_block_index < len(blocks):
            context = self._create_rendering_context(
                blocks, current_block_index, indent_level
            )
            await self._renderer_chain.handle(context)

            if context.markdown_result:
                rendered_block_parts.append(context.markdown_result)

            current_block_index += 1

        result = self._join_rendered_blocks(rendered_block_parts, indent_level)
        result = self._post_processor.process(result)

        return result

    def _create_rendering_context(
        self, blocks: list[Block], block_index: int, indent_level: int
    ) -> MarkdownRenderingContext:
        block = blocks[block_index]
        return MarkdownRenderingContext(
            block=block,
            indent_level=indent_level,
            convert_children_callback=self.convert,
        )

    def _join_rendered_blocks(
        self, rendered_parts: list[str], indent_level: int
    ) -> str:
        separator = "\n\n" if indent_level == 0 else "\n"
        return separator.join(rendered_parts)
