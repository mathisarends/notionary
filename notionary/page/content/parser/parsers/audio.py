"""Parser for audio blocks."""

import re
from typing import override

from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import (
    CreateAudioBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class AudioParser(LineParser):
    """Handles audio blocks with [audio](url) syntax."""

    AUDIO_PATTERN = re.compile(r"\[audio\]\(([^)]+)\)")
    CAPTION_PATTERN = re.compile(r"\(caption:([^)]+)\)")

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self.AUDIO_PATTERN.search(context.line.strip()) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_audio_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_audio_block(self, text: str) -> CreateAudioBlock | None:
        """Create an audio block from markdown text."""
        audio_path = self._extract_audio_path(text.strip())
        if not audio_path:
            return None

        # Extract caption
        caption_text = self._extract_caption(text.strip())
        caption_rich_text = self._build_caption_rich_text(caption_text or "")

        # Only support external URLs
        audio_data = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=audio_path),
            caption=caption_rich_text,
        )

        return CreateAudioBlock(audio=audio_data)

    def _extract_audio_path(self, text: str) -> str | None:
        """Extract audio path/URL from text, handling caption patterns."""
        clean_text = self._remove_caption(text)
        match = self.AUDIO_PATTERN.search(clean_text)
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
