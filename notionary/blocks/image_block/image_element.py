from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import (
    ExternalFile,
    FileType,
    FileUploadFile,
)
from notionary.blocks.image_block.image_models import CreateImageBlock, FileBlock
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.mixins.file_upload.file_upload_mixin import FileUploadMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType


class ImageElement(BaseBlockElement, CaptionMixin, FileUploadMixin):
    """
    Handles conversion between Markdown images and Notion image blocks.

    Supports both external URLs and local image file uploads.

    Markdown image syntax:
    - [image](https://example.com/image.jpg) - External URL
    - [image](./local/photo.png) - Local image file (will be uploaded)
    - [image](C:\Pictures\avatar.jpg) - Absolute local path (will be uploaded)
    - [image](https://example.com/image.jpg)(caption:This is a caption) - URL with caption
    - (caption:Profile picture)[image](./avatar.jpg) - Caption before URL
    """

    # Pattern matches both URLs and file paths
    IMAGE_PATTERN = re.compile(r"\[image\]\(([^)]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.IMAGE and block.image

    @classmethod
    async def markdown_to_notion(cls, text: str) -> Optional[BlockCreateResult]:
        """Convert markdown image syntax to Notion ImageBlock."""
        image_path = cls._extract_image_path(text.strip())
        if not image_path:
            return None

        cls.logger.info(f"Processing image: {image_path}")

        # Extract caption
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Determine if it's a local file or external URL
        if cls._is_local_file_path(image_path):
            cls.logger.debug(f"Detected local image file: {image_path}")

            # Upload the local image file using mixin method
            file_upload_id = await cls._upload_local_file(image_path, "image")
            if not file_upload_id:
                cls.logger.error(f"Failed to upload image: {image_path}")
                return None

            image_block = FileBlock(
                type=FileType.FILE_UPLOAD,
                file_upload=FileUploadFile(id=file_upload_id),
                caption=caption_rich_text,
            )

        else:
            cls.logger.debug(f"Using external image URL: {image_path}")

            image_block = FileBlock(
                type=FileType.EXTERNAL,
                external=ExternalFile(url=image_path),
                caption=caption_rich_text,
            )

        return CreateImageBlock(image=image_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.IMAGE or not block.image:
            return None

        fo = block.image

        # Determine the source for markdown
        if fo.type == FileType.EXTERNAL and fo.external:
            source = fo.external.url
        elif fo.type == FileType.FILE and fo.file:
            source = fo.file.url
        else:
            return None

        result = f"[image]({source})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(fo.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for image blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Image blocks display images from external URLs or upload local image files with optional captions",
            syntax_examples=[
                "[image](https://example.com/photo.jpg)",
                "[image](./local/screenshot.png)",
                "[image](C:\\Pictures\\avatar.jpg)",
                "[image](https://example.com/diagram.png)(caption:Architecture Diagram)",
                "(caption:Sales Chart)[image](./chart.svg)",
                "[image](./screenshot.png)(caption:Dashboard **overview**)",
            ],
            usage_guidelines="Use for displaying images from external URLs or local files. Local image files will be automatically uploaded to Notion. Supports common image formats (jpg, png, gif, svg, webp, bmp, tiff, heic). Caption supports rich text formatting and describes the image content.",
        )

    @classmethod
    def _extract_image_path(cls, text: str) -> Optional[str]:
        """Extract image path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        match = cls.IMAGE_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
