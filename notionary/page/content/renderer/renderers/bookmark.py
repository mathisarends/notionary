from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.renderers.captioned_block import (
    CaptionedBlockRenderer,
)


class BookmarkRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.BOOKMARK

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_bookmark_url(block)

        if not url:
            return ""

        syntax = self._syntax_registry.get_bookmark_syntax()
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    def _extract_bookmark_url(self, block: Block) -> str:
        if not block.bookmark:
            return ""
        return block.bookmark.url or ""
