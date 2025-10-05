"""Parser for video blocks."""

import re
from typing import override

from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import (
    CreateVideoBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class VideoParser(LineParser):
    """Handles video blocks with [video](url) syntax."""

    VIDEO_PATTERN = re.compile(r"\[video\]\(([^)]+)\)")
    CAPTION_PATTERN = re.compile(r"\(caption:([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.VIDEO_PATTERN.search(context.line.strip()) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_video_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_video_block(self, text: str) -> CreateVideoBlock | None:
        """Create a video block from markdown text."""
        video_path = self._extract_video_path(text.strip())
        if not video_path:
            return None

        # Extract caption
        caption_text = self._extract_caption(text.strip())
        caption_rich_text = self._build_caption_rich_text(caption_text or "")

        # Only support external URLs
        video_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=video_path),
            caption=caption_rich_text,
        )

        return CreateVideoBlock(video=video_data)

    def _extract_video_path(self, text: str) -> str | None:
        """Extract video path/URL from text, handling caption patterns."""
        clean_text = self._remove_caption(text)
        match = self.VIDEO_PATTERN.search(clean_text)
        return match.group(1).strip() if match else None

    def _extract_caption(self, text: str) -> str | None:
        """Extract caption text from markdown."""
        caption_match = self.CAPTION_PATTERN.search(text)
        return caption_match.group(1) if caption_match else None

    def _remove_caption(self, text: str) -> str:
        """Remove caption pattern from text."""
        return self.CAPTION_PATTERN.sub("", text).strip()

    def _build_caption_rich_text(self, caption: str) -> list[RichText]:
        """Build rich text list from caption string."""
        if not caption or not caption.strip():
            return []
        return [RichText.from_plain_text(caption.strip())]
