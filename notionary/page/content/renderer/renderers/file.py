from typing import override

from notionary.blocks.schemas import Block, BlockType, ExternalFileWithCaption, NotionHostedFileWithCaption
from notionary.page.content.renderer.renderers.captioned_block import CaptionedBlockRenderer


class FileRenderer(CaptionedBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.FILE

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_file_url(block)

        if not url:
            return ""

        syntax = self._syntax_registry.get_file_syntax()
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    def _extract_file_url(self, block: Block) -> str:
        if not block.file:
            return ""

        if isinstance(block.file, ExternalFileWithCaption):
            return block.file.external.url or ""
        elif isinstance(block.file, NotionHostedFileWithCaption):
            return block.file.file.url or ""

        return ""

    def _extract_file_name(self, block: Block) -> str:
        if not block.file:
            return ""

        if block.file.name:
            return block.file.name or ""

        return ""
