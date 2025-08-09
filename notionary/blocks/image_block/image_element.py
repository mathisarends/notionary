from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import (
    Block,
)
from notionary.blocks.file.file_element_models import ExternalFile, FileObject
from notionary.blocks.image_block.image_models import CreateImageBlock, FileBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.prompts import ElementPromptBuilder, ElementPromptContent


class ImageElement(NotionBlockElement):
    """
    Handles conversion between Markdown images and Notion image blocks.

    Markdown image syntax:
    - [image](https://example.com/image.jpg) - URL only
    - [image](https://example.com/image.jpg "Caption") - URL + caption
    """

    PATTERN = re.compile(
        r"^\[image\]\("  # prefix
        r"(https?://[^\s\"]+)"  # URL (exclude whitespace and ")
        r"(?:\s+\"([^\"]+)\")?"  # optional caption
        r"\)$"
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "image" and block.image is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown image syntax to Notion ImageBlock followed by an empty paragraph."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        url, caption_text = m.group(1), m.group(2) or ""
        # Build ImageBlock
        image_block = FileBlock(
            type="external", external=ExternalFile(url=url), caption=[]
        )
        if caption_text.strip():
            rt = RichTextObject.from_plain_text(caption_text.strip())
            image_block.caption = [rt]

        empty_para = ParagraphBlock(rich_text=[])

        return [
            CreateImageBlock(image=image_block),
            CreateParagraphBlock(paragraph=empty_para),
        ]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "image" or block.image is None:
            return None
        file_object: FileObject = block.image
        # extract URL
        if file_object.type == "external" and file_object.external:
            url = file_object.external.url
        elif file_object.type == "file" and file_object.file:
            url = file_object.file.url
        else:
            return None
        # captions
        captions = file_object.caption or []
        if not captions:
            return f"[image]({url})"
        # compile caption text
        parts: list[str] = []
        for rt in captions:
            # use plain_text if available, otherwise formatted
            parts.append(
                rt.plain_text
                or TextInlineFormatter.extract_text_with_formatting([rt.model_dump()])
            )
        caption = "".join(parts)
        return f'[image]({url} "{caption}")'

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds an image from an external URL or Notion-hosted file."
            )
            .with_usage_guidelines(
                "Use images to include visual content like diagrams, charts, screenshots, or photos."
            )
            .with_syntax('[image](https://example.com/image.jpg "Optional caption")')
            .with_examples(
                [
                    "[image](https://example.com/chart.png)",
                    '[image](https://example.com/photo.jpg "A beautiful sunrise")',
                ]
            )
            .build()
        )
