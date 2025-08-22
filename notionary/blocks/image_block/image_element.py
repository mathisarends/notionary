from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import ExternalFile, FileType
from notionary.blocks.image_block.image_models import CreateImageBlock, FileBlock
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class ImageElement(BaseBlockElement):
    """
    Handles conversion between Markdown images and Notion image blocks.

    Markdown image syntax:
    - [image](https://example.com/image.jpg) - URL only
    - [image](https://example.com/image.jpg "Caption") - URL + caption
    """

    PATTERN = re.compile(
        r"^\[image\]\("  # prefix
        r"(https?://[^\s\"]+)"  # URL (exclude whitespace and ")
        r"(?:\s+\"([^\"]+)\")?"  # optional caption
        r"\)$"
    )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.IMAGE and block.image

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown image syntax to Notion ImageBlock followed by an empty paragraph."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        url, caption_text = match.group(1), match.group(2) or ""
        # Build ImageBlock
        image_block = FileBlock(
            type="external", external=ExternalFile(url=url), caption=[]
        )
        if caption_text.strip():
            rt = RichTextObject.from_plain_text(caption_text.strip())
            image_block.caption = [rt]

        return CreateImageBlock(image=image_block)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.IMAGE or not block.image:
            return None

        fo = block.image

        if fo.type == FileType.EXTERNAL and fo.external:
            url = fo.external.url
        elif fo.type == FileType.FILE and fo.file:
            url = fo.file.url
        else:
            return None

        captions = fo.caption or []
        if not captions:
            return f"[image]({url})"

        caption_text = "".join(
            (rt.plain_text or TextInlineFormatter.extract_text_with_formatting([rt]))
            for rt in captions
        )

        return f'[image]({url} "{caption_text}")'

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for image blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Image blocks display images from external URLs with optional captions",
            syntax_examples=[
                "[image](https://example.com/photo.jpg)",
                '[image](https://example.com/diagram.png "Architecture Diagram")',
                '[image](https://example.com/chart.svg "Sales Chart")',
            ],
            usage_guidelines="Use for displaying images from external URLs. Supports common image formats (jpg, png, gif, svg, webp). Caption describes the image content.",
        )
