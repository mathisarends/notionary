from typing import override

from notionary.blocks.schemas import Block, BlockType, ExternalFileWithCaption, NotionHostedFileWithCaption
from notionary.page.content.renderer.renderers.file_like_block import FileLikeBlockRenderer
from notionary.page.content.syntax.definition import SyntaxDefinition


class ImageRenderer(FileLikeBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.IMAGE

    @override
    def _get_syntax(self) -> SyntaxDefinition:
        return self._syntax_registry.get_image_syntax()

    @override
    def _get_file_data(self, block: Block) -> ExternalFileWithCaption | NotionHostedFileWithCaption | None:
        return block.image
