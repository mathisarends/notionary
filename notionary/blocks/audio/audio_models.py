from typing import Optional
from pydantic import BaseModel

from notionary.blocks.shared.models import RichTextObject


# TODO: Diesen Kram hier auch verwenden
class ExternalAudioSource(BaseModel):
    """External audio source."""

    url: str


class NotionAudioData(BaseModel):
    """Audio block data."""

    type: str = "external"
    external: ExternalAudioSource
    caption: list[dict] = []


class NotionAudioBlock(BaseModel):
    """Audio block result."""

    type: str = "audio"
    audio: NotionAudioData


# Updated method with typed return
@classmethod
def markdown_to_notion(cls, text: str) -> Optional[NotionAudioBlock]:
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

    # Build caption list
    caption_list = []
    if caption_text:
        caption_rich_text = RichTextObject.from_plain_text(caption_text)
        caption_list = [caption_rich_text.model_dump()]

    # Create typed result
    return NotionAudioBlock(
        audio=NotionAudioData(
            external=ExternalAudioSource(url=url), caption=caption_list
        )
    )
