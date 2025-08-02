import re
from typing import Optional

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import Block, HeadingBlock
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


class HeadingElement(NotionBlockElement):
    """Handles conversion between Markdown headings and Notion heading blocks."""

    # Pattern: 1–3 „#“, dann mindestens ein Leerzeichen, dann Text
    PATTERN = re.compile(r"^(#{1,3})[ \t]+(.+)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        m = cls.PATTERN.match(text)
        return bool(m and m.group(2).strip())

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return (
            block.type in ("heading_1", "heading_2", "heading_3")
            and getattr(block, block.type) is not None
        )

    @classmethod
    def markdown_to_notion(cls, text: str) -> HeadingBlock | None:
        """Convert markdown headings (#, ##, ###) to Notion HeadingBlock."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        level = len(m.group(1))
        if level < 1 or level > 3:
            return None

        content = m.group(2).strip()
        if not content:
            return None

        rich_text = TextInlineFormatter.parse_inline_formatting(content)
        # Map markdown heading levels to Notion HeadingBlock
        return HeadingBlock(rich_text=rich_text, color="default", is_toggleable=False)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if not block.type.startswith("heading_"):
            return None

        try:
            level = int(block.type.split("_", 1)[1])
        except (ValueError, IndexError):
            return None

        heading_obj = getattr(block, block.type)
        if not heading_obj or not heading_obj.rich_text:
            return None

        text = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in heading_obj.rich_text]
        )
        if not text:
            return None

        return f"{'#' * level} {text}"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Use Markdown headings (#, ##, ###) to structure content hierarchically."
            )
            .with_usage_guidelines(
                "Use to group content into sections and define a clear hierarchy."
            )
            .with_avoidance_guidelines(
                "Only H1–H3 are supported; deeper levels are not available in Notion."
            )
            .with_standard_markdown()
            .build()
        )
