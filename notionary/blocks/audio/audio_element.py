from __future__ import annotations
import re
from typing import Any, Optional, TYPE_CHECKING


from notionary.blocks.audio.audio_models import CreateAudioBlock
from notionary.blocks.block_models import Block, BlockType
from notionary.blocks.file.file_element_models import FileObject
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.models.notion_page_response import ExternalFile
from notionary.prompts import ElementPromptBuilder, ElementPromptContent

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult


class AudioElement(NotionBlockElement):
    """
    Handles conversion between Markdown audio embeds and Notion audio blocks.

    Markdown audio syntax:
    - [audio](https://example.com/audio.mp3) - Simple audio embed
    - [audio](https://example.com/audio.mp3 "Caption text") - Audio with optional caption

    Where:
    - URL is the required audio file URL
    - Caption is optional descriptive text (enclosed in quotes)
    """

    # Regex patterns
    URL_PATTERN = r"(https?://[^\s\"]+)"
    CAPTION_PATTERN = r'(?:\s+"([^"]+)")?'
    PATTERN = re.compile(r"^\[audio\]\(" + URL_PATTERN + CAPTION_PATTERN + r"\)$")

    # Supported audio extensions
    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".oga", ".m4a"}

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        text = text.strip()
        m = cls.PATTERN.match(text)
        if not m:
            return False
        url = m.group(1)
        return cls._is_likely_audio_url(url)

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == "audio"

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown audio embed to Notion audio block."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        url = m.group(1)
        caption_text = m.group(2)
        if not url:
            return None

        # Create caption rich text objects
        caption_objects = []
        if caption_text:
            caption_rt = RichTextObject.from_plain_text(caption_text)
            caption_objects = [caption_rt]

        # Create AudioBlock content object
        audio_content = FileObject(
            type="external", external=ExternalFile(url=url), caption=caption_objects
        )

        return CreateAudioBlock(audio=audio_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion audio block to markdown audio embed."""
        if block.type != BlockType.AUDIO or block.audio is None:
            return None

        audio = block.audio

        # Only handle external audio
        if audio.type != "external" or audio.external is None:
            return None
        url = audio.external.url
        if not url:
            return None

        # Extract caption
        captions = audio.caption or []
        if captions:
            # captionsof RichTextObject
            caption_text = cls._extract_text_content(
                [rt.model_dump() for rt in captions]
            )
            return f'[audio]({url} "{caption_text}")'

        return f"[audio]({url})"

    @classmethod
    def _is_likely_audio_url(cls, url: str) -> bool:
        return any(url.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)

    @classmethod
    def _extract_text_content(cls, rich: dict[str, Any]) -> str:
        text = ""
        for obj in rich:
            if obj.get("type") == "text":
                text += obj.get("text", {}).get("content", "")
            else:
                text += obj.get("plain_text", "")
        return text

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Embeds an audio file playable directly in the page.")
            .with_usage_guidelines(
                "Use for sound files, music, podcasts or voice recordings; supports MP3, WAV, OGG, M4A."
            )
            .with_syntax('[audio](https://example.com/audio.mp3 "Optional caption")')
            .with_examples(
                [
                    "[audio](https://example.com/song.mp3)",
                    '[audio](https://example.com/podcast.mp3 "Episode 1: Intro")',
                    '[audio](https://example.com/effect.wav "Sound effect")',
                ]
            )
            .with_avoidance_guidelines(
                "Ensure URLs end in supported extensions; some browsers may not play all formats."
            )
            .build()
        )
