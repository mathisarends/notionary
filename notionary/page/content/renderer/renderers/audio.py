from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.renderers.captioned_block import CaptionedBlockRenderer


class AudioRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.AUDIO

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_audio_url(block)

        if not url:
            return ""

        syntax = self._syntax_registry.get_audio_syntax()
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    def _extract_audio_url(self, block: Block) -> str:
        if not block.audio:
            return ""

        if block.audio.external:
            return block.audio.external.url or ""
        elif block.audio.file:
            return block.audio.file.url or ""

        return ""
