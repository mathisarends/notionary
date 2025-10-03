import re
from pathlib import Path
from typing import ClassVar

from notionary.blocks.mappings.base import BaseBlockElement
from notionary.blocks.mappings.mixins.caption_mixin import CaptionMixin
from notionary.blocks.mappings.mixins.file_upload_mixin import FileUploadMixin
from notionary.blocks.schemas import (
    Block,
    BlockCreateResult,
    BlockType,
    CreateVideoBlock,
    ExternalFile,
    FileBlock,
    FileType,
    FileUploadFile,
)
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class VideoElement(BaseBlockElement, CaptionMixin, FileUploadMixin):
    r"""
    Handles conversion between Markdown video embeds and Notion video blocks.

    Supports external URLs (YouTube, Vimeo, direct links) and local video file uploads.

    Markdown video syntax:
    - [video](https://example.com/video.mp4) - External URL
    - [video](./local/movie.mp4) - Local video file (will be uploaded)
    - [video](C:\Videos\tutorial.mov) - Absolute local path (will be uploaded)
    - [video](https://youtube.com/watch?v=abc123)(caption:Demo Video) - URL with caption
    - (caption:Tutorial video)[video](./local.mp4) - Caption before URL
    """

    # Pattern matches both URLs and file paths
    VIDEO_PATTERN = re.compile(r"\[video\]\(([^)]+)\)")

    YOUTUBE_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]{11})"),
        re.compile(r"(?:https?://)?(?:www\.)?youtu\.be/([\w-]{11})"),
    ]

    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".mkv",
        ".m4v",
        ".3gp",
    }

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.VIDEO and block.video

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult | None:
        """Convert markdown video syntax to a Notion VideoBlock."""
        # Extract the path/URL
        path = cls._extract_video_path(text.strip())
        if not path:
            return None

        # Check if it's a local file path
        if cls._is_local_file_path(path):
            # Verify file exists and has supported extension
            video_path = Path(path)
            if not video_path.exists():
                cls.logger.warning(f"Video file not found: {path}")
                return None

            if video_path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
                cls.logger.warning(f"Unsupported video format: {video_path.suffix}")
                return None

            cls.logger.info(f"Uploading local video file: {path}")

            # Upload the local video file
            file_upload_id = await cls._upload_local_file(path, "video")
            if not file_upload_id:
                cls.logger.error(f"Failed to upload video file: {path}")
                return None

            cls.logger.info(f"Successfully uploaded video file with ID: {file_upload_id}")

            # Use mixin to extract caption (if present anywhere in text)
            caption_text = cls.extract_caption(text.strip())
            caption_rich_text = cls.build_caption_rich_text(caption_text or "")

            video_block = FileBlock(
                type=FileType.FILE_UPLOAD,
                file_upload=FileUploadFile(id=file_upload_id),
                caption=caption_rich_text,
            )

            return CreateVideoBlock(video=video_block)

        else:
            # Handle external URL (YouTube, Vimeo, direct links)
            url = path

            # Check for YouTube and normalize URL
            vid_id = cls._get_youtube_id(url)
            if vid_id:
                url = f"https://www.youtube.com/watch?v={vid_id}"

            # Use mixin to extract caption (if present anywhere in text)
            caption_text = cls.extract_caption(text.strip())
            caption_rich_text = cls.build_caption_rich_text(caption_text or "")

            video_block = FileBlock(
                type=FileType.EXTERNAL,
                external=ExternalFile(url=url),
                caption=caption_rich_text,
            )

            return CreateVideoBlock(video=video_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.VIDEO or not block.video:
            return None

        fo = block.video
        url = None

        # Handle both external URLs and uploaded files
        if fo.type == FileType.EXTERNAL and fo.external:
            url = fo.external.url
        elif fo.type == FileType.FILE and fo.file:
            url = fo.file.url

        if not url:
            return None

        result = f"[video]({url})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(fo.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def _get_youtube_id(cls, url: str) -> str | None:
        for pat in cls.YOUTUBE_PATTERNS:
            m = pat.match(url)
            if m:
                return m.group(1)
        return None

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for video blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Video blocks embed videos from external URLs (YouTube, Vimeo, direct links) or upload local video files with optional captions",
            syntax_examples=[
                "[video](https://youtube.com/watch?v=abc123)",
                "[video](https://vimeo.com/123456789)",
                "[video](./local/tutorial.mp4)",
                "[video](C:\\Videos\\presentation.mov)",
                "[video](https://example.com/video.mp4)(caption:Demo Video)",
                "(caption:Tutorial)[video](./demo.mp4)",
                "[video](./training.mp4)(caption:**Important** tutorial)",
            ],
            usage_guidelines="Use for embedding videos from supported platforms or local video files. Supports YouTube, Vimeo, direct video URLs, and local file uploads. Supports common video formats (mp4, avi, mov, wmv, flv, webm, mkv, m4v, 3gp). Caption supports rich text formatting and describes the video content.",
        )

    @classmethod
    def _extract_video_path(cls, text: str) -> str | None:
        """Extract video path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        # Now extract the path/URL from clean text
        match = cls.VIDEO_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
