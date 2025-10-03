import re
from typing import ClassVar

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.mixins.captions import CaptionMixin
from notionary.blocks.schemas import (
    Block,
    BlockType,
    CreateAudioBlock,
    ExternalFile,
    FileData,
    FileType,
)
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class AudioMapper(NotionMarkdownMapper, CaptionMixin):
    AUDIO_PATTERN = re.compile(r"\[audio\]\(([^)]+)\)")
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".mp3", ".wav", ".ogg", ".oga", ".m4a"}

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.AUDIO

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateAudioBlock | None:
        path = cls._extract_audio_path(text.strip())
        if not path:
            return None

        # Use mixin to extract caption (if present anywhere in text)
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Only support external URLs - no local file upload
        audio_content = FileData(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=path),
            caption=caption_rich_text,
        )

        return CreateAudioBlock(audio=audio_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        """Convert Notion audio block to markdown audio embed."""
        if block.type != BlockType.AUDIO or block.audio is None:
            return None

        audio = block.audio
        url = None

        # Handle external URLs
        if audio.type == FileType.EXTERNAL and audio.external is not None:
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
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Audio blocks embed audio files from external URLs or local files with optional captions",
            syntax_examples=[
                "[audio](https://example.com/song.mp3)",
                "[audio](https://example.com/podcast.wav)(caption:Episode 1)",
                "(caption:Background music)[audio](https://example.com/song.mp3)",
                "[audio](https://example.com/interview.mp3)(caption:**Live** interview)",
            ],
            usage_guidelines="Use for embedding audio files like music, podcasts, or sound effects. Supports external URLs only. Caption supports rich text formatting and is optional.",
        )

    @classmethod
    def _is_likely_audio_url(cls, url: str) -> bool:
        return any(url.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)

    @classmethod
    def _extract_audio_path(cls, text: str) -> str | None:
        clean_text = cls.remove_caption(text)

        match = cls.AUDIO_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
