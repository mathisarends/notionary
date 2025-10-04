from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.handler.captioned_block import CaptionedBlockRenderer


class ImageRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.IMAGE

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_image_url(block)

        if not url:
            return ""

        return f"![image]({url})"

    def _extract_image_url(self, block: Block) -> str:
        if not block.image:
            return ""

        if block.image.external:
            return block.image.external.url or ""
        elif block.image.file:
            return block.image.file.url or ""

        return ""
