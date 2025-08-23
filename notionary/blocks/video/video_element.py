from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import ExternalFile, FileBlock, FileType
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult
from notionary.blocks.types import BlockType
from notionary.blocks.video.video_element_models import CreateVideoBlock


class VideoElement(BaseBlockElement, CaptionMixin):
    """
    Handles conversion between Markdown video embeds and Notion video blocks.

    Markdown video syntax:
    - [video](https://example.com/video.mp4) - URL only
    - [video](https://example.com/video.mp4)(caption:Demo Video) - URL with caption
    - (caption:Tutorial video)[video](https://youtube.com/watch?v=abc123) - caption before URL

    Supports YouTube, Vimeo, and direct file URLs.
    """

    # Flexible pattern that can handle caption in any position
    VIDEO_PATTERN = re.compile(r"\[video\]\((https?://[^\s\"]+)\)")

    YOUTUBE_PATTERNS = [
        re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]{11})"),
        re.compile(r"(?:https?://)?(?:www\.)?youtu\.be/([\w-]{11})"),
    ]

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.VIDEO and block.video

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown video syntax to a Notion VideoBlock."""
        # Use our own regex to find the video URL
        video_match = cls.VIDEO_PATTERN.search(text.strip())
        if not video_match:
            return None

        url = video_match.group(1)

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
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.VIDEO or not block.video:
            return None

        fo = block.video

        # URL ermitteln
        if fo.type == FileType.EXTERNAL and fo.external:
            url = fo.external.url
        elif fo.type == FileType.FILE and fo.file:
            url = fo.file.url
        else:
            return None  # (file_upload o.ä. hier nicht supported)

        result = f"[video]({url})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(fo.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def _get_youtube_id(cls, url: str) -> Optional[str]:
        for pat in cls.YOUTUBE_PATTERNS:
            m = pat.match(url)
            if m:
                return m.group(1)
        return None

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for video blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Video blocks embed videos from external URLs like YouTube, Vimeo, or direct video files",
            syntax_examples=[
                "[video](https://youtube.com/watch?v=abc123)",
                "[video](https://vimeo.com/123456789)",
                "[video](https://example.com/video.mp4)(caption:Demo Video)",
                "(caption:Tutorial)[video](https://youtu.be/abc123)",
                "[video](https://youtube.com/watch?v=xyz)(caption:**Important** tutorial)",
            ],
            usage_guidelines="Use for embedding videos from supported platforms or direct video file URLs. Supports YouTube, Vimeo, and direct video files. Caption supports rich text formatting and describes the video content.",
        )
