import re
from typing import Dict, Any, Optional, List
from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class EmbedElement(NotionBlockElement):
    """
    Handles conversion between Markdown embeds and Notion embed blocks.

    Markdown embed syntax (custom format):
    - <embed:Caption>(https://example.com) - Basic embed with caption
    - <embed>(https://example.com) - Embed without caption

    Supports various URL types including websites, PDFs, Google Maps, Google Drive,
    Twitter/X posts, and other sources that Notion can embed.
    """

    PATTERN = re.compile(
        r"^<embed(?:\:(.*?))?>(?:\s*)" + r'\((https?://[^\s"]+)' + r"\)$"
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown embed."""
        text = text.strip()
        return text.startswith("<embed") and bool(EmbedElement.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion embed."""
        return block.get("type") == "embed"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown embed to Notion embed block."""
        embed_match = EmbedElement.PATTERN.match(text.strip())
        if not embed_match:
            return None

        caption = embed_match.group(1) or ""
        url = embed_match.group(2)

        if not url:
            return None

        # Prepare the embed block
        embed_block = {
            "type": "embed",
            "embed": {"url": url},
        }

        # Add caption if provided
        if caption:
            embed_block["embed"]["caption"] = [
                {"type": "text", "text": {"content": caption}}
            ]

        return embed_block

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion embed block to markdown embed."""
        if block.get("type") != "embed":
            return None

        embed_data = block.get("embed", {})
        url = embed_data.get("url", "")

        if not url:
            return None

        # Extract caption if available
        caption = ""
        caption_rich_text = embed_data.get("caption", [])
        if caption_rich_text:
            caption = EmbedElement._extract_text_content(caption_rich_text)

        if caption:
            return f"<embed:{caption}>({url})"

        return f"<embed>({url})"

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
        return {
            "description": "Embeds external content from websites, PDFs, Google Maps, and other sources directly in your document.",
            "when_to_use": (
                "Use embeds when you want to include external content that isn't just a video or image. "
                "Embeds are great for interactive content, reference materials, or live data sources."
            ),
            "syntax": "<embed:Caption>(https://example.com)",
            "examples": [
                "<embed:Course materials>(https://drive.google.com/file/d/123456/view)",
                "<embed:Our office location>(https://www.google.com/maps?q=San+Francisco)",
                "<embed:Latest announcement>(https://twitter.com/NotionHQ/status/1234567890)",
                "<embed:Project documentation>(https://github.com/username/repo)",
                "<embed>(https://example.com/important-reference.pdf)",
            ],
        }
