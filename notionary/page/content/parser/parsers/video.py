"""Parser for video blocks."""

from typing import override

from notionary.blocks.schemas import (
    CreateVideoBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser
from notionary.page.content.syntax.service import SyntaxRegistry


class VideoParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_video_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._syntax.regex_pattern.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        video_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=[],
        )
        block = CreateVideoBlock(video=video_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self._syntax.regex_pattern.search(line)
        return match.group(1).strip() if match else None
