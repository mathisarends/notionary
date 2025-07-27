from __future__ import annotations
from typing import Optional
import re

from notionary.blocks import (
    NotionBlockElement,
    ElementPromptBuilder,
    ElementPromptContent,
    NotionBlockResult,
)


class AudioElement(NotionBlockElement):
    """
    Handles conversion between Markdown audio embeds and Notion audio blocks.

    Markdown audio syntax (custom format since standard Markdown doesn't support audio):
    - $[Caption](https://example.com/audio.mp3) - Basic audio with caption
    - $[](https://example.com/audio.mp3) - Audio without caption
    - $[Caption](https://storage.googleapis.com/audio_summaries/example.mp3) - CDN hosted audio

    Supports various audio URLs including direct audio file links from CDNs and other sources.
    """

    PATTERN = re.compile(r"^\$\[(.*?)\]" + r'\((https?://[^\s"]+)' + r"\)$")

    AUDIO_EXTENSIONS = [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"]

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown audio embed."""
        text = text.strip()
        return text.startswith("$[") and bool(cls.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: dict[str, any]) -> bool:
        """Check if block is a Notion audio."""
        return block.get("type") == "audio"

    @classmethod
    def is_audio_url(cls, url: str) -> bool:
        """Check if URL points to an audio file."""
        return (
            any(url.lower().endswith(ext) for ext in cls.AUDIO_EXTENSIONS)
            or "audio" in url.lower()
            or "storage.googleapis.com/audio_summaries" in url.lower()
        )

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown audio embed to Notion audio block."""
        audio_match = cls.PATTERN.match(text.strip())
        if not audio_match:
            return None

        caption = audio_match.group(1)
        url = audio_match.group(2)

        if not url:
            return None

        # Make sure this is an audio URL
        if not cls.is_audio_url(url):
            # If not obviously an audio URL, we'll still accept it as the user might know better
            pass

        # Prepare the audio block
        audio_block = {
            "type": "audio",
            "audio": {"type": "external", "external": {"url": url}},
        }

        # Add caption if provided
        if caption:
            audio_block["audio"]["caption"] = [
                {"type": "text", "text": {"content": caption}}
            ]

        return audio_block

    @classmethod
    def notion_to_markdown(cls, block: dict[str, any]) -> Optional[str]:
        """Convert Notion audio block to markdown audio embed."""
        if block.get("type") != "audio":
            return None

        audio_data = block.get("audio", {})

        # Handle both external and file (uploaded) audios
        if audio_data.get("type") == "external":
            url = audio_data.get("external", {}).get("url", "")
        elif audio_data.get("type") == "file":
            url = audio_data.get("file", {}).get("url", "")
        else:
            return None

        if not url:
            return None

        # Extract caption if available
        caption = ""
        caption_rich_text = audio_data.get("caption", [])
        if caption_rich_text:
            caption = cls._extract_text_content(caption_rich_text)

        return f"$[{caption}]({url})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Audio embeds are single-line elements."""
        return False

    @classmethod
    def _extract_text_content(cls, rich_text: List[dict[str, any]]) -> str:
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
        """Returns information for LLM prompts about this element."""
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds audio content from external sources like CDNs or direct audio URLs."
            )
            .with_syntax("$[Caption](https://example.com/audio.mp3)")
            .with_examples(
                [
                    "$[Podcast Episode](https://storage.googleapis.com/audio_summaries/ep_ai_summary_127d02ec-ca12-4312-a5ed-cb14b185480c.mp3)",
                    "$[Voice recording](https://example.com/audio/recording.mp3)",
                    "$[](https://storage.googleapis.com/audio_summaries/example.mp3)",
                ]
            )
            .with_usage_guidelines(
                "Use audio embeds when you want to include audio content directly in your document. "
                "Audio embeds are useful for podcasts, music, voice recordings, or any content that benefits from audio explanation."
            )
            .build()
        )
