from typing import override

from notionary.blocks.schemas import Block, BlockType, ExternalFileWithCaption, NotionHostedFileWithCaption
from notionary.page.content.renderer.renderers.file_like_block import FileLikeBlockRenderer
from notionary.page.content.syntax import SyntaxDefinition


class FileRenderer(FileLikeBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.FILE

    @override
    def _get_syntax(self) -> SyntaxDefinition:
        return self._syntax_registry.get_file_syntax()

    @override
    def _get_file_data(self, block: Block) -> ExternalFileWithCaption | NotionHostedFileWithCaption | None:
        return block.file

    def _extract_file_name(self, block: Block) -> str:
        if not block.file:
            return ""

        if block.file.name:
            return block.file.name or ""

        return ""
