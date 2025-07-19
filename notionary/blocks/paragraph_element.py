from typing import Dict, Any, Optional

from notionary.blocks import NotionBlockElement
from notionary.prompting.element_prompt_content import (
    ElementPromptBuilder,
    ElementPromptContent,
)
from notionary.blocks.text_inline_formatter import TextInlineFormatter


class ParagraphElement(NotionBlockElement):
    """Handles conversion between Markdown paragraphs and Notion paragraph blocks."""

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """
        Check if text is a markdown paragraph.
        Paragraphs are essentially any text that isn't matched by other block elements.
        Since paragraphs are the fallback element, this always returns True.
        """
        return True

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion paragraph."""
        return block.get("type") == "paragraph"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown paragraph to Notion paragraph block."""
        if not text.strip():
            return None

        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": TextInlineFormatter.parse_inline_formatting(text)
            },
        }

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion paragraph block to markdown paragraph."""
        if block.get("type") != "paragraph":
            return None

        paragraph_data = block.get("paragraph", {})
        rich_text = paragraph_data.get("rich_text", [])

        text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        return text if text else None

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the paragraph element,
        including information about supported inline formatting.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates standard paragraph blocks for regular text content with support for inline formatting: "
                "**bold**, *italic*, `code`, ~~strikethrough~~, __underline__, and [links](url)."
            )
            .with_usage_guidelines(
                "Use for normal text content. Paragraphs are the default block type when no specific formatting is applied. "
                "Apply inline formatting to highlight key points or provide links to resources."
            )
            .with_syntax("Just write text normally without any special prefix")
            .with_examples(
                [
                    "This is a simple paragraph with plain text.",
                    "This paragraph has **bold** and *italic* formatting.",
                    "You can include [links](https://example.com) or `inline code`.",
                    "Advanced formatting: ~~strikethrough~~ and __underlined text__.",
                ]
            )
            .build()
        )
