from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import ExternalFile, FileBlock, FileType
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.pdf.pdf_models import CreatePdfBlock


class PdfElement(BaseBlockElement, CaptionMixin):
    """
    Handles conversion between Markdown PDF embeds and Notion PDF blocks.

    Markdown PDF syntax:
    - [pdf](https://example.com/document.pdf) - External URL
    - [pdf](https://example.com/document.pdf)(caption:Annual Report 2024) - URL with caption
    - (caption:User Manual)[pdf](https://example.com/manual.pdf) - caption before URL
    - [pdf](notion://file_id_here)(caption:Notion hosted file) - Notion hosted file
    - [pdf](upload://upload_id_here)(caption:File upload) - File upload

    Supports all three PDF types: external, notion-hosted, and file uploads.
    """

    # Flexible pattern that can handle caption in any position
    PDF_PATTERN = re.compile(r"\[pdf\]\(((?:https?://|notion://|upload://)[^\s\"]+)\)")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        # Notion PDF block covers PDFs
        return block.type == BlockType.PDF and block.pdf

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown PDF link to Notion FileBlock (used for PDF)."""
        # Use our own regex to find the PDF URL
        pdf_match = cls.PDF_PATTERN.search(text.strip())
        if not pdf_match:
            return None

        url = pdf_match.group(1)

        # Use mixin to extract caption (if present anywhere in text)
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")

        # Build FileBlock using FileType enum (reused for PDF)
        pdf_block = FileBlock(
            type=FileType.EXTERNAL,
            external=ExternalFile(url=url),
            caption=caption_rich_text,
        )

        return CreatePdfBlock(pdf=pdf_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.PDF or not block.pdf:
            return None

        pb: FileBlock = block.pdf

        # Determine URL (only external and file types are valid for Markdown)
        if pb.type == FileType.EXTERNAL and pb.external:
            url = pb.external.url
        elif pb.type == FileType.FILE and pb.file:
            url = pb.file.url
        elif pb.type == FileType.FILE_UPLOAD:
            # Uploaded PDF has no stable URL for Markdown
            return None
        else:
            return None

        result = f"[pdf]({url})"

        # Add caption if present
        caption_markdown = cls.format_caption_for_markdown(pb.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for PDF blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="PDF blocks embed and display PDF documents from external URLs with optional captions",
            syntax_examples=[
                "[pdf](https://example.com/document.pdf)",
                "[pdf](https://example.com/report.pdf)(caption:Annual Report 2024)",
                "(caption:User Manual)[pdf](https://example.com/manual.pdf)",
                "[pdf](https://example.com/guide.pdf)(caption:**Important** documentation)",
            ],
            usage_guidelines="Use for embedding PDF documents that can be viewed inline. Supports external URLs and Notion-hosted files. Caption supports rich text formatting and should describe the PDF content.",
        )
