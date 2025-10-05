"""Parser for bookmark blocks."""

import re
from typing import override

from notionary.blocks.schemas import BookmarkData, CreateBookmarkBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser


class BookmarkParser(LineParser):
    BOOKMARK_PATTERN = re.compile(r"\[bookmark\]\((https?://[^\s\"]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.BOOKMARK_PATTERN.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        url = self._extract_url(context.line)
        if not url:
            return

        bookmark_data = BookmarkData(url=url, caption=[])
        block = CreateBookmarkBlock(bookmark=bookmark_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self.BOOKMARK_PATTERN.search(line)
        return match.group(1) if match else None
