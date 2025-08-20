from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.audio.audio_models import CreateAudioBlock
from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import ExternalFile, FileBlock, FileType
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class AudioElement(BaseBlockElement):
    """
    Handles conversion between Markdown audio embeds and Notion audio blocks.

    Markdown audio syntax:
    - [audio](https://example.com/audio.mp3) - Simple audio embed
    - [audio](https://example.com/audio.mp3 "Caption text") - Audio with optional caption

    Where:
    - URL is the required audio file URL
    - Caption is optional descriptive text (enclosed in quotes)
    """

    URL_PATTERN = r"(https?://[^\s\"]+)"
    CAPTION_PATTERN = r'(?:\s+"([^"]+)")?'
    PATTERN = re.compile(r"^\[audio\]\(" + URL_PATTERN + CAPTION_PATTERN + r"\)$")

    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".oga", ".m4a"}

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.AUDIO

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown audio embed to Notion audio block (or return None if not matching)."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None
        url = match.group(1)

        if not cls._is_likely_audio_url(url):
            return None
        caption_text = match.group(2)

        # Create caption rich text objects
        caption_objects = []
        if caption_text:
            caption_rt = RichTextObject.from_plain_text(caption_text)
            caption_objects = [caption_rt]

        audio_content = FileBlock(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=caption_objects,
        )

        return CreateAudioBlock(audio=audio_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion audio block to markdown audio embed."""
        if block.type != BlockType.AUDIO or block.audio is None:
            return None

        audio = block.audio

        # Only handle external audio
        if audio.type != FileType.EXTERNAL or audio.external is None:
            return None
        url = audio.external.url
        if not url:
            return None

        # Extract caption
        captions = audio.caption or []
        if captions:
            # use TextInlineFormatter instead of manual extraction
            caption_text = TextInlineFormatter.extract_text_with_formatting(captions)
            return f'[audio]({url} "{caption_text}")'

        return f"[audio]({url})"

    @classmethod
    def _is_likely_audio_url(cls, url: str) -> bool:
        return any(url.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)
