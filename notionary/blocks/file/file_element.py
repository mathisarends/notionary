from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import (
    CreateFileBlock,
    ExternalFile,
    FileBlock,
    FileType,
    FileUploadFile,
)
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.mixins.file_upload.file_upload_mixin import FileUploadMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType


class FileElement(BaseBlockElement, CaptionMixin, FileUploadMixin):
    """
    Handles conversion between Markdown file embeds and Notion file blocks.

    Supports both external URLs and local file uploads.

    Markdown file syntax:
    - [file](https://example.com/document.pdf) - External URL
    - [file](./local/document.pdf) - Local file (will be uploaded)
    - [file](C:\Documents\report.pdf) - Absolute local path (will be uploaded)
    - [file](https://example.com/document.pdf)(caption:Annual Report) - With caption
    - (caption:Important document)[file](./doc.pdf) - Caption before URL
    """

    FILE_PATTERN = re.compile(r"\[file\]\(([^)]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return bool(block.type == BlockType.FILE and block.file)

    @classmethod
    async def markdown_to_notion(cls, text: str) -> Optional[BlockCreateResult]:
        """Convert markdown file link to Notion FileBlock."""
        file_path = cls._extract_file_path(text.strip())
        if not file_path:
            return None

        cls.logger.info(f"Processing file: {file_path}")

        # Extract caption
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Determine if it's a local file or external URL
        if cls._is_local_file_path(file_path):
            cls.logger.debug(f"Detected local file: {file_path}")

            # Upload the local file using mixin method
            file_upload_id = await cls._upload_local_file(file_path, "file")
            if not file_upload_id:
                cls.logger.error(f"Failed to upload file: {file_path}")
                return None

            # Create FILE_UPLOAD block
            file_block = FileBlock(
                type=FileType.FILE_UPLOAD,
                file_upload=FileUploadFile(id=file_upload_id),
                caption=caption_rich_text,
                name=Path(file_path).name,
            )

        else:
            cls.logger.debug(f"Using external URL: {file_path}")

            file_block = FileBlock(
                type=FileType.EXTERNAL,
                external=ExternalFile(url=file_path),
                caption=caption_rich_text,
            )

        return CreateFileBlock(file=file_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.FILE or not block.file:
            return None

        fb: FileBlock = block.file

        # Determine the source for markdown
        if fb.type == FileType.EXTERNAL and fb.external:
            source = fb.external.url
        elif fb.type == FileType.FILE and fb.file:
            source = fb.file.url
        else:
            return None

        result = f"[file]({source})"

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
            description="File blocks embed files from external URLs or upload local files with optional captions",
            syntax_examples=[
                "[file](https://example.com/document.pdf)",
                "[file](./local/document.pdf)",
                "[file](C:\\Documents\\report.xlsx)",
                "[file](https://example.com/document.pdf)(caption:Annual Report)",
                "(caption:Q1 Data)[file](./spreadsheet.xlsx)",
                "[file](./manual.docx)(caption:**User** manual)",
            ],
            usage_guidelines="Use for both external URLs and local files. Local files will be automatically uploaded to Notion. Supports various file formats including PDFs, documents, spreadsheets, images. Caption supports rich text formatting and should describe the file content or purpose.",
        )

    @classmethod
    def _extract_file_path(cls, text: str) -> Optional[str]:
        """Extract file path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)

        match = cls.FILE_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()

        return None
