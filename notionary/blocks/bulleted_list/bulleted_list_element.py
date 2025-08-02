import re
from typing import Optional

from notionary.blocks import NotionBlockElement
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import Block
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter
from notionary.models.notion_block_response import BulletedListItemBlock


class BulletedListElement(NotionBlockElement):
    """Class for converting between Markdown bullet lists and Notion bulleted list items."""

    # Regex for markdown bullets (excluding todo items [ ] or [x])
    PATTERN = re.compile(r"^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text.rstrip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return (
            block.type == "bulleted_list_item" and block.bulleted_list_item is not None
        )

    @classmethod
    def markdown_to_notion(cls, text: str) -> BulletedListItemBlock:
        """
        Convert a markdown bulleted list item into a Notion BulletedListItemBlock.
        """
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        # Extract the content part (second capture group)
        content = m.group(2)

        # Parse inline markdown formatting into RichTextObject list
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        # Return a properly typed Notion block
        return BulletedListItemBlock(rich_text=rich_text, color="default")

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion bulleted list item block to markdown."""
        if block.type != "bulleted_list_item" or block.bulleted_list_item is None:
            return None
        # extract rich_text list of RichTextObject
        rich_list = block.bulleted_list_item.rich_text
        # convert to markdown with inline formatting
        text = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in rich_list]
        )
        return f"- {text}"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description("Creates bulleted list items for unordered lists.")
            .with_usage_guidelines(
                "Use for lists where order doesn't matter, such as features, options, or items without hierarchy."
            )
            .with_syntax("- Item text")
            .with_standard_markdown()
            .build()
        )
