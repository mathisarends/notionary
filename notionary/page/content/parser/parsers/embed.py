"""Parser for embed blocks."""

import re
from typing import override

from notionary.blocks.schemas import CreateEmbedBlock, EmbedData
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.captioned_block_parser import (
    CaptionedBlockParser,
)


class EmbedParser(CaptionedBlockParser):
    EMBED_PATTERN = re.compile(r"\[embed\]\((https?://[^\s\"]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.EMBED_PATTERN.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        """Process embed block and check for caption on next line."""
        url = self._extract_url(context.line)
        if not url:
            return

        caption_rich_text = await self._extract_caption_for_single_line_block(context)

        embed_data = EmbedData(url=url, caption=caption_rich_text)
        block = CreateEmbedBlock(embed=embed_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.EMBED_PATTERN.search(line)
        return match.group(1) if match else None
