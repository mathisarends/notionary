from __future__ import annotations

import re
from pathlib import Path

from notionary.blocks.audio.audio_models import CreateAudioBlock
from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import (
    ExternalFile,
    FileBlock,
    FileType,
    FileUploadFile,
)
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.mixins.file_upload.file_upload_mixin import FileUploadMixin
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.util.logging_mixin import LoggingMixin


class AudioElement(BaseBlockElement, FileUploadMixin, LoggingMixin, CaptionMixin):
    r"""
    Handles conversion between Markdown audio embeds and Notion audio blocks.

    Supports both external URLs and local audio file uploads.

    Markdown audio syntax:
    - [audio](https://example.com/audio.mp3) - External URL
    - [audio](./local/song.mp3) - Local audio file (will be uploaded)
    - [audio](C:\Music\podcast.wav) - Absolute local path (will be uploaded)
    - [audio](https://example.com/audio.mp3)(caption:Episode 1) - URL with caption
    """

    AUDIO_PATTERN = re.compile(r"\[audio\]\(([^)]+)\)")
    SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".oga", ".m4a"}

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.AUDIO

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult | None:
        """Convert markdown audio embed to Notion audio block."""
        # Extract the path/URL
        path = cls._extract_audio_path(text.strip())
        if not path:
            return None

        # Check if it's a local file path
        if cls._is_local_file_path(path):
            # Verify file exists and has supported extension
            audio_path = Path(path)
            if not audio_path.exists():
                cls.logger.warning(f"Audio file not found: {path}")
                return None

            if audio_path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
                cls.logger.warning(f"Unsupported audio format: {audio_path.suffix}")
                return None

            cls.logger.info(f"Uploading local audio file: {path}")

            # Upload the local audio file
            file_upload_id = await cls._upload_local_file(path, "audio")
            if not file_upload_id:
                cls.logger.error(f"Failed to upload audio file: {path}")
                return None

            cls.logger.info(
                f"Successfully uploaded audio file with ID: {file_upload_id}"
            )

            # Use mixin to extract caption (if present anywhere in text)
            caption_text = cls.extract_caption(text.strip())
            caption_rich_text = cls.build_caption_rich_text(caption_text or "")

            audio_content = FileBlock(
                type=FileType.FILE_UPLOAD,
                file_upload=FileUploadFile(id=file_upload_id),
                caption=caption_rich_text,
            )

            return CreateAudioBlock(audio=audio_content)

        else:
            # Handle external URL - accept any URL (validation happens at API level)
            # Use mixin to extract caption (if present anywhere in text)
            caption_text = cls.extract_caption(text.strip())
            caption_rich_text = cls.build_caption_rich_text(caption_text or "")

            audio_content = FileBlock(
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

        # Handle both external URLs and uploaded files
        if audio.type == FileType.EXTERNAL and audio.external is not None:
            url = audio.external.url
        elif audio.type == FileType.FILE_UPLOAD and audio.file_upload is not None:
            url = audio.file_upload.url

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
        """Get system prompt information for audio blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Audio blocks embed audio files from external URLs or local files with optional captions",
            syntax_examples=[
                "[audio](https://example.com/song.mp3)",
                "[audio](./local/podcast.wav)",
                "[audio](C:\\Music\\interview.mp3)",
                "[audio](https://example.com/podcast.wav)(caption:Episode 1)",
                "(caption:Background music)[audio](./song.mp3)",
                "[audio](./interview.mp3)(caption:**Live** interview)",
            ],
            usage_guidelines="Use for embedding audio files like music, podcasts, or sound effects. Supports both external URLs and local file uploads. Supports common audio formats (mp3, wav, ogg, m4a). Caption supports rich text formatting and is optional.",
        )

    @classmethod
    def _is_likely_audio_url(cls, url: str) -> bool:
        return any(url.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)

    @classmethod
    def _extract_audio_path(cls, text: str) -> str | None:
        """Extract audio path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        match = cls.AUDIO_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
