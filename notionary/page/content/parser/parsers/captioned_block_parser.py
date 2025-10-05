import re

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.rich_text.models import RichText
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class CaptionedBlockParser(LineParser):
    CAPTION_LINE_PATTERN = re.compile(r"^\[caption\]\s+(.+)$")

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    async def _extract_caption_for_single_line_block(self, context: BlockParsingContext) -> list[RichText]:
        return await self._extract_caption_at_index(context, index=0)

    async def _extract_caption_for_multi_line_block(
        self, context: BlockParsingContext, lines_consumed: int
    ) -> list[RichText]:
        return await self._extract_caption_at_index(context, index=lines_consumed)

    async def _extract_caption_at_index(self, context: BlockParsingContext, index: int) -> list[RichText]:
        remaining_lines = context.get_remaining_lines()

        if len(remaining_lines) <= index:
            return []

        caption_line = remaining_lines[index].strip()
        caption_match = self.CAPTION_LINE_PATTERN.match(caption_line)

        if not caption_match:
            return []

        caption_text = caption_match.group(1)
        context.lines_consumed += 1
        return await self._rich_text_converter.to_rich_text(caption_text)
