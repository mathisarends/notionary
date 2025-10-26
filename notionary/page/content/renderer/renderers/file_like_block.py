from abc import abstractmethod
from typing import override

from notionary.blocks.schemas import (
    Block,
    ExternalFileWithCaption,
    NotionHostedFileWithCaption,
)
from notionary.page.content.renderer.renderers.captioned_block import (
    CaptionedBlockRenderer,
)
from notionary.page.content.syntax.definition import EnclosedSyntaxDefinition


class FileLikeBlockRenderer(CaptionedBlockRenderer):
    @abstractmethod
    def _get_syntax(self) -> EnclosedSyntaxDefinition:
        pass

    @abstractmethod
    def _get_file_data(
        self, block: Block
    ) -> ExternalFileWithCaption | NotionHostedFileWithCaption | None:
        pass

    @override
    async def _render_main_content(self, block: Block) -> str:
        url = self._extract_url(block)

        if not url:
            return ""

        syntax = self._get_syntax()
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    def _extract_url(self, block: Block) -> str:
        file_data = self._get_file_data(block)

        if not file_data:
            return ""

        if isinstance(file_data, ExternalFileWithCaption):
            return file_data.external.url or ""
        elif isinstance(file_data, NotionHostedFileWithCaption):
            return file_data.file.url or ""

        return ""
