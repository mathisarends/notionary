import re
from typing import Dict, Any, Optional, List
from notionary.core.converters.elements.notion_block_element import NotionBlockElement


class AudioElement(NotionBlockElement):
    """
    Handles conversion between Markdown audio embeds and Notion audio blocks.

    Markdown audio syntax (custom format since standard Markdown doesn't support audio):
    - $[Caption](https://example.com/audio.mp3) - Basic audio with caption
    - $[](https://example.com/audio.mp3) - Audio without caption
    - $[Caption](https://storage.googleapis.com/audio_summaries/example.mp3) - CDN hosted audio

    Supports various audio URLs including direct audio file links from CDNs and other sources.
    """

    # Regex pattern for audio syntax
    PATTERN = re.compile(
        r"^\$\[(.*?)\]"  # $[Caption] part
        + r'\((https?://[^\s"]+)'  # (URL part
        + r"\)$"  # closing parenthesis
    )

    # Audio file extensions
    AUDIO_EXTENSIONS = [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"]

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown audio embed."""
        text = text.strip()
        return text.startswith("$[") and bool(AudioElement.PATTERN.match(text))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion audio."""
        return block.get("type") == "audio"

    @staticmethod
    def is_audio_url(url: str) -> bool:
        """Check if URL points to an audio file."""
        return (
            any(url.lower().endswith(ext) for ext in AudioElement.AUDIO_EXTENSIONS)
            or "audio" in url.lower()
            or "storage.googleapis.com/audio_summaries" in url.lower()
        )

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown audio embed to Notion audio block."""
        audio_match = AudioElement.PATTERN.match(text.strip())
        if not audio_match:
            return None

        caption = audio_match.group(1)
        url = audio_match.group(2)

        if not url:
            return None

        # Make sure this is an audio URL
        if not AudioElement.is_audio_url(url):
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

    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
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
            caption = AudioElement._extract_text_content(caption_rich_text)

        return f"$[{caption}]({url})"

    @staticmethod
    def is_multiline() -> bool:
        """Audio embeds are single-line elements."""
        return False

    @staticmethod
    def _extract_text_content(rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result

    @classmethod
    def get_llm_prompt_content(cls) -> dict:
        """Returns information for LLM prompts about this element."""
        return {
            "description": "Embeds audio content from external sources like CDNs or direct audio URLs.",
            "when_to_use": "Use audio embeds when you want to include audio content directly in your document. Audio embeds are useful for podcasts, music, voice recordings, or any content that benefits from audio explanation.",
            "syntax": [
                "$[](https://example.com/audio.mp3) - Audio without caption",
                "$[Caption text](https://example.com/audio.mp3) - Audio with caption",
            ],
            "supported_sources": [
                "Direct links to audio files (.mp3, .wav, .ogg, etc.)",
                "Google Cloud Storage links (storage.googleapis.com)",
                "Other audio hosting platforms supported by Notion",
            ],
            "examples": [
                "$[Podcast Episode](https://storage.googleapis.com/audio_summaries/ep_ai_summary_127d02ec-ca12-4312-a5ed-cb14b185480c.mp3)",
                "$[Voice recording](https://example.com/audio/recording.mp3)",
                "$[](https://storage.googleapis.com/audio_summaries/example.mp3)",
            ],
        }
