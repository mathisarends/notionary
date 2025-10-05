"""Parser for embed blocks."""

import re
from typing import override

from notionary.blocks.schemas import CreateEmbedBlock, EmbedData
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser


class EmbedParser(LineParser):
    EMBED_PATTERN = re.compile(r"\[embed\]\((https?://[^\s\"]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.EMBED_PATTERN.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        embed_data = EmbedData(url=url, caption=[])
        block = CreateEmbedBlock(embed=embed_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.EMBED_PATTERN.search(line)
        return match.group(1) if match else None
