from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import (
    CreateFileBlock,
    ExternalFile,
    FileBlock,
    FileType,
)
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.mixins.file_upload.file_upload_mixin import FileUploadMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType


class FileElement(BaseBlockElement, CaptionMixin, FileUploadMixin):
    """
    Handles conversion between Markdown file embeds and Notion file blocks.

    Markdown file syntax:
    - [file](https://example.com/document.pdf) - URL only
    - [file](https://example.com/document.pdf)(caption:Annual Report) - URL with caption
    - (caption:Important document)[file](https://example.com/doc.pdf) - caption before URL

    Supports external file URLs with optional captions.
    """

    FILE_PATTERN = re.compile(r"\[file\]\((https?://[^\s\"]+)\)")

    @classmethod
    def _extract_file_url(cls, text: str) -> Optional[str]:
        """Extract file URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        # Now extract the URL from clean textw
        match = cls.FILE_PATTERN.search(clean_text)
        if match:
            return match.group(1)

        return None

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.FILE and block.file

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown file link to Notion FileBlock."""
        print("before url")
        url = cls._extract_file_url(text.strip())
        if not url:
            return None
        
        context = cls._get_file_upload_client()

        # Use mixin to extract caption (if present anywhere in text)
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Build FileBlock using FileType enum
        file_block = FileBlock(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=caption_rich_text,
        )

        return CreateFileBlock(file=file_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.FILE or not block.file:
            return None

        fb: FileBlock = block.file

        # Determine URL (only external and file types are valid for Markdown)
        if fb.type == FileType.EXTERNAL and fb.external:
            url = fb.external.url
        elif fb.type == FileType.FILE and fb.file:
            url = fb.file.url
        elif fb.type == FileType.FILE_UPLOAD:
            # Uploaded file has no stable URL for Markdown
            return None
        else:
            return None

        result = f"[file]({url})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(fb.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for file blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="File blocks embed downloadable files from external URLs with optional captions",
            syntax_examples=[
                "[file](https://example.com/document.pdf)",
                "[file](https://example.com/document.pdf)(caption:Annual Report)",
                "(caption:Q1 Data)[file](https://example.com/spreadsheet.xlsx)",
                "[file](https://example.com/manual.docx)(caption:**User** manual)",
            ],
            usage_guidelines="Use for linking to downloadable files like PDFs, documents, spreadsheets. Supports various file formats. Caption supports rich text formatting and should describe the file content or purpose.",
        )