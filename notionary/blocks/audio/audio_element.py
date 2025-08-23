from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.audio.audio_models import CreateAudioBlock
from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import ExternalFile, FileBlock, FileType
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType


class AudioElement(BaseBlockElement, CaptionMixin):
    """
    Handles conversion between Markdown audio embeds and Notion audio blocks.

    Markdown audio syntax:
    - [audio](https://example.com/audio.mp3) - Simple audio embed
    - [audio](https://example.com/audio.mp3)(caption:Episode 1) - Audio with caption
    - (caption:Background music)[audio](https://example.com/song.mp3) - caption before URL

    Where:
    - URL is the required audio file URL
    - Caption supports rich text formatting and is optional
    """

    # Simple pattern that matches just the audio link, CaptionMixin handles caption separately
    AUDIO_PATTERN = re.compile(r"\[audio\]\((https?://[^\s\"]+)\)")

    @classmethod
    def _extract_audio_url(cls, text: str) -> Optional[str]:
        """Extract audio URL from text, handling caption patterns."""
        # First remove any captions to get clean text for URL extraction
        clean_text = cls.remove_caption(text)

        # Now extract the URL from clean text
        match = cls.AUDIO_PATTERN.search(clean_text)
        if match:
            return match.group(1)

        return None

    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".oga", ".m4a"}

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.AUDIO

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown audio embed to Notion audio block."""
        # Use our helper method to extract the URL
        url = cls._extract_audio_url(text.strip())
        if not url:
            return None

        if not cls._is_likely_audio_url(url):
            return None

        # Use mixin to extract caption (if present anywhere in text)
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        audio_content = FileBlock(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=caption_rich_text,
        )

        return CreateAudioBlock(audio=audio_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
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

        result = f"[audio]({url})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(audio.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for audio blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Audio blocks embed audio files from external URLs with optional captions",
            syntax_examples=[
                "[audio](https://example.com/song.mp3)",
                "[audio](https://example.com/podcast.wav)(caption:Episode 1)",
                "(caption:Background music)[audio](https://soundcloud.com/track/123)",
                "[audio](https://example.com/interview.mp3)(caption:**Live** interview)",
            ],
            usage_guidelines="Use for embedding audio files like music, podcasts, or sound effects. Supports common audio formats (mp3, wav, ogg, m4a). Caption supports rich text formatting and is optional.",
        )

    @classmethod
    def _is_likely_audio_url(cls, url: str) -> bool:
        return any(url.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)
