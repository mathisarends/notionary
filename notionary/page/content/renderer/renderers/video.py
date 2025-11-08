from typing import override

from notionary.blocks.schemas import (
    Block,
    BlockType,
    ExternalFileWithCaption,
    NotionHostedFileWithCaption,
)
from notionary.markdown.syntax.definition.models import EnclosedSyntaxDefinition
from notionary.page.content.renderer.renderers.file_like_block import (
    FileLikeBlockRenderer,
)


class VideoRenderer(FileLikeBlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.VIDEO

    @override
    def _get_syntax(self) -> EnclosedSyntaxDefinition:
        return self._syntax_registry.get_video_syntax()

    @override
    def _get_file_data(
        self, block: Block
    ) -> ExternalFileWithCaption | NotionHostedFileWithCaption | None:
        return block.video
