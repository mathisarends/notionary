from typing import Optional

from notionary.blocks import NotionBlockElement
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import Block, ParagraphBlock
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


class ParagraphElement(NotionBlockElement):
    """
    Handles conversion between Markdown paragraphs and Notion paragraph blocks.
    """

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(text and text.strip())

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "paragraph" and block.paragraph is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> ParagraphBlock | None:
        """Convert markdown text to a Notion ParagraphBlock."""
        # Skip empty text
        if not text.strip():
            return None

        rich = TextInlineFormatter.parse_inline_formatting(text)

        return ParagraphBlock(rich_text=rich, color="default")

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "paragraph" or block.paragraph is None:
            return None
        rich_list = block.paragraph.rich_text
        markdown = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in rich_list]
        )
        return markdown or None

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates standard paragraph blocks for text with support for inline formatting."
            )
            .with_usage_guidelines(
                "Use for normal text. Applies **bold**, *italic*, `code`, ~~strikethrough~~, __underline__, and links."
            )
            .with_syntax("Just write text normally without prefix")
            .with_examples(
                [
                    "This is a simple paragraph.",
                    "Paragraph with **bold** and [link](https://example.com).",
                ]
            )
            .build()
        )
