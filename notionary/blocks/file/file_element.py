from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

from notionary.blocks.file.file_element_models import (
    CreateFileBlock,
    ExternalFile,
    FileBlock,
    FileType
)
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.block_models import (
    Block,
    BlockType,
)
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.prompts import ElementPromptContent, ElementPromptBuilder

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult


class FileElement(NotionBlockElement):
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
    def match_markdown(cls, text: str) -> bool:
        txt = text.strip()
        return txt.startswith("[file]") and bool(cls.PATTERN.match(txt))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        # Notion file block covers files
        return block.type == BlockType.FILE and block.file

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown file link to Notion FileBlock followed by an empty paragraph."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        url, caption_text = m.group(1), m.group(2) or ""

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

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds external files (PDFs, Word/Excel docs, etc.) via Notion file blocks."
            )
            .with_usage_guidelines(
                "Use file embeds to share reports, manuals, or any cloud-hosted files with optional captions."
            )
            .with_syntax('[file](https://example.com/doc.pdf "Caption")')
            .build()
        )
