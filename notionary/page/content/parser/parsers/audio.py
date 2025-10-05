"""Parser for audio blocks."""

import re
from typing import override

from notionary.blocks.schemas import (
    CreateAudioBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.captioned_block_parser import (
    CaptionedBlockParser,
)


class AudioParser(CaptionedBlockParser):
    AUDIO_PATTERN = re.compile(r"\[audio\]\(([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.AUDIO_PATTERN.search(context.line.strip()) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        caption_rich_text = await self._extract_caption_for_single_line_block(context)

        audio_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=caption_rich_text,
        )
        block = CreateAudioBlock(audio=audio_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.AUDIO_PATTERN.search(line.strip())
        return match.group(1).strip() if match else None
