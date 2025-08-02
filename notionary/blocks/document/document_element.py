import re
from typing import Any, Optional, List

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import Block, FileObject, RichTextObject


class DocumentElement(NotionBlockElement):
    """
    Handles conversion between Markdown document embeds and Notion file blocks.

    Markdown document syntax:
    - [document](https://example.com/document.pdf "Caption")
    - [document](https://example.com/document.pdf)

    Supports external file URLs with optional captions.
    """

    PATTERN = re.compile(
        r"^\[document\]\("  # prefix
        r'(https?://[^\s\)"]+)'  # URL
        r'(?:\s+"([^"]*)")?'  # optional caption
        r"\)$"
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        txt = text.strip()
        return txt.startswith("[document]") and bool(cls.PATTERN.match(txt))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        # Notion file block covers documents
        return block.type == "file" and block.file is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[List[Any]]:
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None
        url, caption = m.group(1), m.group(2) or ""

        file_data: dict[str, Any] = {"type": "external", "external": {"url": url}}
        if caption:
            rt = RichTextObject.from_plain_text(caption)
            file_data["caption"] = [rt.model_dump()]
        else:
            file_data["caption"] = []

        file_block = {"type": "file", "file": file_data}
        empty_para = {"type": "paragraph", "paragraph": {"rich_text": []}}
        return [file_block, empty_para]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "file" or block.file is None:
            return None
        fo: FileObject = block.file
        url = ""
        if fo.type == "external" and fo.external:
            url = fo.external.url
        elif fo.type == "file" and fo.file:
            url = fo.file.url
        if not url:
            return None
        captions = fo.caption or []
        if not captions:
            return f"[document]({url})"
        text = "".join(
            rt.plain_text if hasattr(rt, "plain_text") else rt.text.content
            for rt in captions
        )
        return f'[document]({url} "{text}")'

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds external document files (PDFs, Word/Excel docs) via Notion file blocks."
            )
            .with_usage_guidelines(
                "Use document embeds to share reports, manuals, or any cloud-hosted files with optional captions."
            )
            .with_syntax('[document](https://example.com/doc.pdf "Caption")')
            .build()
        )
