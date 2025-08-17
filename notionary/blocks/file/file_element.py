from __future__ import annotations
import re
from typing import Optional

from notionary.blocks.file.file_element_models import (
    CreateFileBlock,
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


class FileElement(BaseBlockElement):
    """
    Handles conversion between Markdown file embeds and Notion file blocks.

    Markdown file syntax:
    - [file](https://example.com/document.pdf "Caption")
    - [file](https://example.com/document.pdf)

    Supports external file URLs with optional captions.
    """

    PATTERN = re.compile(
        r"^\[file\]\("  # prefix
        r'(https?://[^\s\)"]+)'  # URL
        r'(?:\s+"([^"]*)")?'  # optional caption
        r"\)$"
    )

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        # Notion file block covers files
        return block.type == BlockType.FILE and block.file

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown file link to Notion FileBlock followed by an empty paragraph."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        url, caption_text = match.group(1), match.group(2) or ""

        # Build FileBlock using FileType enum
        file_block = FileBlock(
            type=FileType.EXTERNAL, external=ExternalFile(url=url), caption=[]
        )
        if caption_text.strip():
            rt = RichTextObject.from_plain_text(caption_text)
            file_block.caption = [rt]

        empty_para = ParagraphBlock(rich_text=[])

        return [
            CreateFileBlock(file=file_block),
            CreateParagraphBlock(paragraph=empty_para),
        ]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
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

        if not fb.caption:
            return f"[file]({url})"

        caption_md = TextInlineFormatter.extract_text_with_formatting(fb.caption)
        if caption_md:
            return f'[file]({url} "{caption_md}")'
        return f"[file]({url})"
