import re
from typing import Any, Optional, List

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import (
    Block,
    ExternalFile,
    FileObject,
    ParagraphBlock,
    RichTextObject,
    VideoBlock,
)
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


class VideoElement(NotionBlockElement):
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
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "video" and block.video is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> list[VideoBlock | ParagraphBlock] | None:
        """Convert markdown video syntax to a Notion VideoBlock plus an empty paragraph."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        url, caption_text = m.group(1), m.group(2) or ""
        # Normalize YouTube URLs by extracting ID
        vid_id = cls._get_youtube_id(url)
        if vid_id:
            url = f"https://www.youtube.com/watch?v={vid_id}"

        # Build VideoBlock
        video_block = VideoBlock(
            type="external", external=ExternalFile(url=url), caption=[]
        )
        if caption_text.strip():
            rt = RichTextObject.from_plain_text(caption_text.strip())
            video_block.caption = [rt]

        # Append an empty paragraph for spacing
        empty_para = ParagraphBlock(rich_text=[])
        return [video_block, empty_para]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "video" or block.video is None:
            return None
        fo: FileObject = block.video
        # extract URL
        if fo.type == "external" and fo.external:
            url = fo.external.url
        elif fo.type == "file" and fo.file:
            url = fo.file.url
        else:
            return None
        # caption
        captions = fo.caption or []
        if not captions:
            return f"[video]({url})"
        parts: List[str] = []
        for rt in captions:
            parts.append(
                rt.plain_text
                or TextInlineFormatter.extract_text_with_formatting([rt.model_dump()])
            )
        caption = "".join(parts)
        return f'[video]({url} "{caption}")'

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def _get_youtube_id(cls, url: str) -> Optional[str]:
        for pat in cls.YOUTUBE_PATTERNS:
            m = pat.match(url)
            if m:
                return m.group(1)
        return None

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds video content from external sources like YouTube or direct video files."
            )
            .with_usage_guidelines(
                "Use video blocks to include tutorials, demos, or any multimedia content inline."
            )
            .with_syntax('[video](https://example.com/video.mp4 "Optional caption")')
            .with_examples(
                [
                    "[video](https://youtu.be/dQw4w9WgXcQ)",
                    '[video](https://example.com/demo.mp4 "Demo video")',
                ]
            )
            .build()
        )
