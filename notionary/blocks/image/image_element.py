import re
from typing import Any, Optional, List

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import Block, RichTextObject, FileObject
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


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
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None
        url, caption = m.group(1), m.group(2)
        # build image object
        img_data: dict[str, Any] = {"type": "external", "external": {"url": url}}
        if caption:
            rt = RichTextObject.from_plain_text(caption)
            img_data["caption"] = [rt.model_dump()]
        else:
            img_data["caption"] = []
        block_out = {"type": "image", "image": img_data}
        # add empty paragraph for spacing
        empty_para = {"type": "paragraph", "paragraph": {"rich_text": []}}
        return [block_out, empty_para]

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
        parts: List[str] = []
        for rt in captions:
            # use plain_text if available, otherwise formatted
            parts.append(
                rt.plain_text
                or TextInlineFormatter.extract_text_with_formatting([rt.model_dump()])
            )
        caption = "".join(parts)
        return f'[image]({url} "{caption}")'

    @classmethod
    def is_multiline(cls) -> bool:
        return False

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
