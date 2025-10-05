"""Parser for embed blocks."""

import re
from typing import override

from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import CreateEmbedBlock, EmbedData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class EmbedParser(LineParser):
    """Handles embed blocks with [embed](url) syntax."""

    PATTERN = re.compile(
        r"^\[embed\]\("  # prefix
        r"(https?://[^\s\"]+)"  # URL
        r"(?:\s+\"([^\"]+)\")?"  # optional caption
        r"\)$"
    )

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.PATTERN.match(context.line.strip()) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_embed_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_embed_block(self, text: str) -> CreateEmbedBlock | None:
        """Create an embed block from markdown text."""
        match = self.PATTERN.match(text.strip())
        if not match:
            return None

        url = match.group(1)
        caption_text = match.group(2) or ""

        # Build embed data
        caption = []
        if caption_text.strip():
            caption = [RichText.from_plain_text(caption_text.strip())]

        embed_data = EmbedData(url=url, caption=caption)
        return CreateEmbedBlock(embed=embed_data)
