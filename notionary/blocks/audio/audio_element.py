import re
from typing import Any, Optional, List

from notionary.blocks import (
    NotionBlockElement,
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)
from notionary.blocks.shared.models import RichTextObject


class AudioElement(NotionBlockElement):
    """
    Handles conversion between Markdown audio embeds and Notion audio blocks.

    Markdown audio syntax:
    - [audio](https://example.com/audio.mp3) - Simple audio embed
    - [audio](https://example.com/audio.mp3 "Caption text") - Audio with caption

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
        m = cls.PATTERN.match(text.strip())
        if not m:
            return False
        url = m.group(1)
        return cls._is_likely_audio_url(url)

    @classmethod
    def match_notion(cls, block: dict[str, Any]) -> bool:
        """Check if block is a Notion audio block."""
        return block.get("type") == "audio"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown audio embed to Notion audio block."""
        audio_match = cls.PATTERN.match(text.strip())
        if not audio_match:
            return None

        url = audio_match.group(1)
        caption_text = audio_match.group(2)

        if not url:
            return None

        # Validate URL if possible
        if not cls._is_likely_audio_url(url):
            # Still proceed - user might know better
            pass

        audio_data = {"type": "external", "external": {"url": url}}

        # Add caption if provided
        if caption_text:
            caption_rich_text = RichTextObject.from_plain_text(caption_text)
            audio_data["caption"] = [caption_rich_text.model_dump()]
        else:
            audio_data["caption"] = []

        return {"type": "audio", "audio": audio_data}

    @classmethod
    def notion_to_markdown(cls, block: dict[str, Any]) -> Optional[str]:
        """Convert Notion audio block to markdown audio embed."""
        if block.get("type") != "audio":
            return None

        audio_data = block.get("audio", {})

        # Get URL from external source
        if audio_data.get("type") == "external":
            url = audio_data.get("external", {}).get("url", "")
        else:
            # Handle file or file_upload types if needed
            return None

        if not url:
            return None

        # Extract caption
        caption = audio_data.get("caption", [])
        if caption:
            caption_text = cls._extract_text_content(caption)
            return f'[audio]({url} "{caption_text}")'

        return f"[audio]({url})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Audio embeds are single-line elements."""
        return False

    @classmethod
    def _is_likely_audio_url(cls, url: str) -> bool:
        """Check if URL likely points to an audio file."""
        return any(url.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)

    @classmethod
    def _extract_text_content(cls, rich_text: List[dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the audio element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds an audio file that can be played directly in the page."
            )
            .with_usage_guidelines(
                "Use audio embeds when you want to include sound files, music, podcasts, "
                "or voice recordings. Supports common audio formats like MP3, WAV, OGG, and M4A."
            )
            .with_syntax('![audio](https://example.com/audio.mp3 "Optional caption")')
            .with_examples(
                [
                    "[audio](https://example.com/song.mp3)",
                    '[audio](https://example.com/podcast.mp3 "Episode 1: Introduction")',
                    '[audio](https://example.com/sound.wav "Sound effect for presentation")',
                    '[audio](https://example.com/recording.m4a "Voice memo from meeting")',
                ]
            )
            .with_avoidance_guidelines(
                "Ensure the URL points to a valid audio file. "
                "Some audio formats may not be supported by all browsers."
            )
            .build()
        )
