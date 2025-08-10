from __future__ import annotations
import re
from typing import Optional

from notionary.blocks.block_models import (
    Block,
    BlockType,
)
from notionary.blocks.embed.embed_models import CreateEmbedBlock, EmbedBlock
from notionary.blocks.file.file_element_models import (
    ExternalFile,
    FileUploadFile,
    NotionHostedFile,
)
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


from notionary.blocks.block_models import Block, BlockCreateResult


class EmbedElement(NotionBlockElement):
    """
    Handles conversion between Markdown embeds and Notion embed blocks.

    Markdown embed syntax:
    - [embed](https://example.com) - URL only
    - [embed](https://example.com "Caption") - URL + caption
    """

    PATTERN = re.compile(
        r"^\[embed\]\("  # prefix
        r"(https?://[^\s\"]+)"  # URL
        r"(?:\s+\"([^\"]+)\")?"  # optional caption
        r"\)$"
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.EMBED and block.embed

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown embed syntax to Notion EmbedBlock."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        url, caption_text = m.group(1), m.group(2) or ""

        # Build EmbedBlock
        embed_block = EmbedBlock(url=url, caption=[])
        if caption_text.strip():
            rt = RichTextObject.from_plain_text(caption_text.strip())
            embed_block.caption = [rt]

        return CreateEmbedBlock(embed=embed_block)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.EMBED or not block.embed:
            return None

        fo = block.embed

        if isinstance(fo, (ExternalFile, NotionHostedFile)):
            url = fo.url
        elif isinstance(fo, FileUploadFile):
            return None
        else:
            return None

        if not fo.caption:
            return f"[embed]({url})"

        text = "".join(
            rt.plain_text or TextInlineFormatter.extract_text_with_formatting([rt])
            for rt in fo.caption
        )

        return f'[embed]({url} "{text}")'
    