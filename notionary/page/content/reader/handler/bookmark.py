from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.handler.captioned_block import CaptionedBlockRenderer


class BookmarkRenderer(CaptionedBlockRenderer):
    BOOKMARK_MARKDOWN_PATTERN = "[bookmark]({url})"

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.BOOKMARK

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_bookmark_url(block)

        if not url:
            return ""

        return self.BOOKMARK_MARKDOWN_PATTERN.format(url=url)

    def _extract_bookmark_url(self, block: Block) -> str:
        if not block.bookmark:
            return ""
        return block.bookmark.url or ""
