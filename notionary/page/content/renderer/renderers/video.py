from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.renderers.captioned_block import CaptionedBlockRenderer


class VideoRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.VIDEO

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_video_url(block)

        if not url:
            return ""

        syntax = self._syntax_registry.get_video_syntax()
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    def _extract_video_url(self, block: Block) -> str:
        if not block.video:
            return ""

        if block.video.external:
            return block.video.external.url or ""
        elif block.video.file:
            return block.video.file.url or ""

        return ""
