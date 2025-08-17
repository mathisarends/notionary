from __future__ import annotations
import re
from typing import Optional

from notionary.blocks.pdf.pdf_models import CreatePdfBlock
from notionary.blocks.file.file_element_models import (
    ExternalFile,
    FileBlock,
    FileType,
)
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

from notionary.blocks.models import Block, BlockCreateResult, BlockType


class PdfElement(BaseBlockElement):
    """
    Handles conversion between Markdown PDF embeds and Notion PDF blocks.

    Markdown PDF syntax:
    - [pdf](https://example.com/document.pdf "Caption")     # External URL
    - [pdf](notion://file_id_here "Caption")                # Notion hosted file
    - [pdf](upload://upload_id_here "Caption")              # File upload
    - [pdf](https://example.com/document.pdf)               # Without caption

    Supports all three PDF types: external, notion-hosted, and file uploads.
    """

    PATTERN = re.compile(
        r"^\[pdf\]\("  # prefix
        r'((?:https?://|notion://|upload://)[^\s\)"]+)'  # URL with protocol
        r'(?:\s+"([^"]*)")?'  # optional caption
        r"\)$"
    )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        # Notion PDF block covers PDFs
        return block.type == BlockType.PDF and block.pdf

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown PDF link to Notion FileBlock (used for PDF) followed by an empty paragraph."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        url, caption_text = match.group(1), match.group(2) or ""

        # Build FileBlock using FileType enum (reused for PDF)
        pdf_block = FileBlock(
            type=FileType.EXTERNAL, external=ExternalFile(url=url), caption=[]
        )
        if caption_text.strip():
            rt = RichTextObject.from_plain_text(caption_text)
            pdf_block.caption = [rt]

        empty_para = ParagraphBlock(rich_text=[])

        return [
            CreatePdfBlock(pdf=pdf_block),
            CreateParagraphBlock(paragraph=empty_para),
        ]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
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

        if not pb.caption:
            return f"[pdf]({url})"

        caption_md = TextInlineFormatter.extract_text_with_formatting(pb.caption)
        if caption_md:
            return f'[pdf]({url} "{caption_md}")'
        return f"[pdf]({url})"
