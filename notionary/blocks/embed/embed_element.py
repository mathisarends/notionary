import re
from typing import Any, Optional, List

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import (
    Block,
    EmbedBlock,
    RichTextObject,
    ExternalFile,
    NotionHostedFile,
    FileUploadFile,
    FileObject,
)
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


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
        return block.type == "embed" and block.embed is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> EmbedBlock | None:
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

        return embed_block

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "embed" or block.embed is None:
            return None
        fo: FileObject = block.embed
        # extract URL
        if isinstance(fo, ExternalFile):
            url = fo.url
        elif isinstance(fo, NotionHostedFile):
            url = fo.url
        elif isinstance(fo, FileUploadFile):
            # file_upload is unsupported for embed
            return None
        else:
            return None
        captions = fo.caption or []
        if not captions:
            return f"[embed]({url})"
        text = "".join(
            (
                rt.plain_text
                if hasattr(rt, "plain_text")
                else TextInlineFormatter.extract_text_with_formatting([rt.model_dump()])
            )
            for rt in captions
        )
        return f'[embed]({url} "{text}")'

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Embeds external content URLs as interactive embeds.")
            .with_usage_guidelines(
                "Use embeds for interactive or reference content; supports captioning."
            )
            .with_syntax('[embed](https://example.com "Caption")')
            .build()
        )
