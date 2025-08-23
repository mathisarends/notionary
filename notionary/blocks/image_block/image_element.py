from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import ExternalFile, FileType
from notionary.blocks.image_block.image_models import CreateImageBlock, FileBlock
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType


class ImageElement(BaseBlockElement, CaptionMixin):
    """
    Handles conversion between Markdown images and Notion image blocks.

    Markdown image syntax:
    - [image](https://example.com/image.jpg) - URL only
    - [image](https://example.com/image.jpg)(caption:This is a caption) - URL with caption
    - (caption:Profile picture)[image](https://example.com/avatar.jpg) - caption before URL
    """

    # Flexible pattern that can handle caption in any position
    IMAGE_PATTERN = re.compile(r"\[image\]\((https?://[^\s\"]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.IMAGE and block.image

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown image syntax to Notion ImageBlock."""
        # First remove captions to get clean text for URL extraction
        clean_text = cls.remove_caption(text.strip())

        # Use our own regex to find the image URL
        image_match = cls.IMAGE_PATTERN.search(clean_text)
        if not image_match:
            return None

        url = image_match.group(1)

        # Use mixin to extract caption (if present anywhere in text)
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Build ImageBlock
        image_block = FileBlock(
            type="external", external=ExternalFile(url=url), caption=caption_rich_text
        )

        return CreateImageBlock(image=image_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.IMAGE or not block.image:
            return None

        fo = block.image

        if fo.type == FileType.EXTERNAL and fo.external:
            url = fo.external.url
        elif fo.type == FileType.FILE and fo.file:
            url = fo.file.url
        else:
            return None

        result = f"[image]({url})"

        # Add caption if present
        caption_markdown = cls.format_caption_for_markdown(fo.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for image blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Image blocks display images from external URLs with optional captions",
            syntax_examples=[
                "[image](https://example.com/photo.jpg)",
                "[image](https://example.com/diagram.png)(caption:Architecture Diagram)",
                "(caption:Sales Chart)[image](https://example.com/chart.svg)",
                "[image](https://example.com/screenshot.png)(caption:Dashboard **overview**)",
            ],
            usage_guidelines="Use for displaying images from external URLs. Supports common image formats (jpg, png, gif, svg, webp). Caption supports rich text formatting and describes the image content.",
        )
