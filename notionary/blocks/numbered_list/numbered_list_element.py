import re
from typing import Any, Optional

from notionary.blocks import NotionBlockElement
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.block_models import (
    Block,
    CreateNumberedListItemBlock,
    NumberedListItemBlock,
)
from notionary.blocks.notion_block_element import BlockCreateResult
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class NumberedListElement(NotionBlockElement):
    """Converts between Markdown numbered lists and Notion numbered list items."""

    PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return (
            block.type == "numbered_list_item" and block.numbered_list_item is not None
        )

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown numbered list item to Notion NumberedListItemBlock."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        content = m.group(2)
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        numbered_list_content = NumberedListItemBlock(
            rich_text=rich_text, color="default"
        )
        return CreateNumberedListItemBlock(numbered_list_item=numbered_list_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "numbered_list_item" or block.numbered_list_item is None:
            return None

        rich = block.numbered_list_item.rich_text
        content = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in rich]
        )
        return f"1. {content}"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Creates numbered list items for ordered sequences.")
            .with_usage_guidelines(
                "Use for lists where order matters, such as steps, rankings, or sequential items."
            )
            .with_syntax("1. Item text")
            .with_standard_markdown()
            .build()
        )
