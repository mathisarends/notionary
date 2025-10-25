from typing import override

from notionary.blocks.schemas import Block, BlockType, ExternalFileWithCaption, NotionHostedFileWithCaption
from notionary.page.content.renderer.renderers.file_like_block import FileLikeBlockRenderer
from notionary.page.content.syntax import SyntaxDefinition


class ImageRenderer(FileLikeBlockRenderer):
    @override
    def _get_block_type(self) -> BlockType:
        return BlockType.IMAGE

    @override
    def _get_syntax(self) -> SyntaxDefinition:
        return self._syntax_registry.get_image_syntax()

    @override
    def _get_file_data(self, block: Block) -> ExternalFileWithCaption | NotionHostedFileWithCaption | None:
        return block.image
