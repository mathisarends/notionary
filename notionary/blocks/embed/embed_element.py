import re
from typing import Dict, Any, Optional, List

from notionary.blocks import NotionBlockElement
from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)


class EmbedElement(NotionBlockElement):
    """
    Handles conversion between Markdown embeds and Notion embed blocks.

    Markdown embed syntax:
    - [embed](https://example.com) - Simple embed with URL only
    - [embed](https://example.com "Caption") - Embed with URL and caption

    Where:
    - URL is the required embed URL
    - Caption is an optional descriptive text (enclosed in quotes)

    Supports various URL types including websites, PDFs, Google Maps, Google Drive,
    Twitter/X posts, and other sources that Notion can embed.
    """

    # Regex pattern for embed syntax with optional caption
    PATTERN = re.compile(
        r"^\[embed\]\("  # [embed]( prefix
        + r'(https?://[^\s"]+)'  # URL (required)
        + r'(?:\s+"([^"]+)")?'  # Optional caption in quotes
        + r"\)$"  # closing parenthesis
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown embed."""
        return text.strip().startswith("[embed]") and bool(
            EmbedElement.PATTERN.match(text.strip())
        )

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion embed."""
        return block.get("type") == "embed"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown embed to Notion embed block."""
        embed_match = EmbedElement.PATTERN.match(text.strip())
        if not embed_match:
            return None

        url = embed_match.group(1)
        caption = embed_match.group(2)

        if not url:
            return None

        embed_data = {"url": url}

        # Add caption if provided
        if caption:
            embed_data["caption"] = [{"type": "text", "text": {"content": caption}}]
        else:
            embed_data["caption"] = []

        # Prepare the embed block
        embed_block = {"type": "embed", "embed": embed_data}

        # Add empty paragraph after embed
        empty_paragraph = {"type": "paragraph", "paragraph": {"rich_text": []}}

        return [embed_block, empty_paragraph]

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion embed block to markdown embed."""
        if block.get("type") != "embed":
            return None

        embed_data = block.get("embed", {})
        url = embed_data.get("url", "")

        if not url:
            return None

        caption_rich_text = embed_data.get("caption", [])

        if not caption_rich_text:
            # Simple embed with URL only
            return f"[embed]({url})"

        # Extract caption text
        caption = EmbedElement._extract_text_content(caption_rich_text)

        if caption:
            return f'[embed]({url} "{caption}")'

        return f"[embed]({url})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Embeds are single-line elements."""
        return False

    @classmethod
    def _extract_text_content(cls, rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the embed element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds external content from websites, PDFs, Google Maps, and other sources directly in your document."
            )
            .with_usage_guidelines(
                "Use embeds when you want to include external content that isn't just a video or image. "
                "Embeds are great for interactive content, reference materials, or live data sources."
            )
            .with_syntax('[embed](https://example.com "Optional caption")')
            .with_examples(
                [
                    "[embed](https://drive.google.com/file/d/123456/view)",
                    '[embed](https://www.google.com/maps?q=San+Francisco "Our office location")',
                    '[embed](https://twitter.com/NotionHQ/status/1234567890 "Latest announcement")',
                    '[embed](https://github.com/username/repo "Project documentation")',
                    '[embed](https://example.com/important-reference.pdf "Course materials")',
                ]
            )
            .build()
        )
