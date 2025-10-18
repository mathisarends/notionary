"""Parser for bookmark blocks."""

from typing import override

from notionary.blocks.schemas import BookmarkData, CreateBookmarkBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser
from notionary.page.content.syntax import SyntaxRegistry


class BookmarkParser(LineParser):
    def __init__(self, syntax_registry: SyntaxRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_bookmark_syntax()

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

        bookmark_data = BookmarkData(url=url, caption=[])
        block = CreateBookmarkBlock(bookmark=bookmark_data)
        context.result_blocks.append(block)

    def _extract_url(self, line: str) -> str | None:
        match = self._syntax.regex_pattern.search(line)
        return match.group(1) if match else None
