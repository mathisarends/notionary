from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import ExternalFile, FileBlock, FileType
from notionary.blocks.models import Block, BlockCreateResult
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.types import BlockType
from notionary.blocks.video.video_element_models import CreateVideoBlock


class VideoElement(BaseBlockElement):
    """
    Handles conversion between Markdown video embeds and Notion video blocks.

    Markdown video syntax:
    - [video](https://example.com/video.mp4) - URL only
    - [video](https://example.com/video.mp4 "Caption") - URL + caption

    Supports YouTube, Vimeo, and direct file URLs.
    """

    PATTERN = re.compile(
        r"^\[video\]\("  # prefix
        r"(https?://[^\s\"]+)"  # URL
        r"(?:\s+\"([^\"]+)\")?"  # optional caption
        r"\)$"
    )

    YOUTUBE_PATTERNS = [
        re.compile(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([\w-]{11})"),
        re.compile(r"(?:https?://)?(?:www\.)?youtu\.be/([\w-]{11})"),
    ]

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.VIDEO and block.video

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown video syntax to a Notion VideoBlock plus an empty paragraph."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        url, caption_text = match.group(1), match.group(2) or ""

        vid_id = cls._get_youtube_id(url)
        if vid_id:
            url = f"https://www.youtube.com/watch?v={vid_id}"

        video_block = FileBlock(
            type=FileType.EXTERNAL, external=ExternalFile(url=url), caption=[]
        )
        if caption_text.strip():
            rt = RichTextObject.from_plain_text(caption_text.strip())
            video_block.caption = [rt]

        return CreateVideoBlock(video=video_block)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
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

        # Captions
        captions = fo.caption or []
        if not captions:
            return f"[video]({url})"

        caption_text = "".join(
            (rt.plain_text or TextInlineFormatter.extract_text_with_formatting([rt]))
            for rt in captions
        )

        return f'[video]({url} "{caption_text}")'

    @classmethod
    def _get_youtube_id(cls, url: str) -> Optional[str]:
        for pat in cls.YOUTUBE_PATTERNS:
            m = pat.match(url)
            if m:
                return m.group(1)
        return None
