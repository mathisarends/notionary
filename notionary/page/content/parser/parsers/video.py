"""Parser for video blocks."""

import re
from typing import override

from notionary.blocks.schemas import (
    CreateVideoBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.captioned_block_parser import (
    CaptionedBlockParser,
)


class VideoParser(CaptionedBlockParser):
    VIDEO_PATTERN = re.compile(r"\[video\]\(([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.VIDEO_PATTERN.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        caption_rich_text = await self._extract_caption_for_single_line_block(context)

        # Create the video block
        video_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=caption_rich_text,
        )
        block = CreateVideoBlock(video=video_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.VIDEO_PATTERN.search(line)
        return match.group(1).strip() if match else None
