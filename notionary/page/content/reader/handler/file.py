from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.handler.captioned_block import CaptionedBlockRenderer


class FileRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.FILE

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_file_url(block)
        name = self._extract_file_name(block)

        if not url:
            return ""

        link_text = name or "file"
        return f"[{link_text}]({url})"

    def _extract_file_url(self, block: Block) -> str:
        if not block.file:
            return ""

        if block.file.external:
            return block.file.external.url or ""
        elif block.file.file:
            return block.file.file.url or ""

        return ""

    def _extract_file_name(self, block: Block) -> str:
        if not block.file:
            return ""

        if block.file.name:
            return block.file.name or ""

        return ""
