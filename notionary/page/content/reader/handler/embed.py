from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.handler.captioned_block import CaptionedBlockRenderer


class EmbedRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.EMBED

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_embed_url(block)

        if not url:
            return ""

        return f"[embed]({url})"

    def _extract_embed_url(self, block: Block) -> str:
        if not block.embed:
            return ""
        return block.embed.url or ""
