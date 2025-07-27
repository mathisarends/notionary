import re
from typing import Dict, Any, Optional, List, Tuple

from notionary.blocks import NotionBlockElement
from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)
from notionary.blocks.shared.models import RichTextObject


class BookmarkElement(NotionBlockElement):
    """
    Handles conversion between Markdown bookmarks and Notion bookmark blocks.

    Markdown bookmark syntax:
    - [bookmark](https://example.com) - Simple bookmark with URL only
    - [bookmark](https://example.com "Title") - Bookmark with URL and title
    - [bookmark](https://example.com "Title" "Description") - Bookmark with URL, title, and description

    Where:
    - URL is the required bookmark URL
    - Title is an optional title (enclosed in quotes)
    - Description is an optional description (enclosed in quotes)
    """

    # Regex pattern for bookmark syntax with optional title and description
    PATTERN = re.compile(
        r"^\[bookmark\]\("  # [bookmark]( prefix
        + r'(https?://[^\s"]+)'  # URL (required)
        + r'(?:\s+"([^"]+)")?'  # Optional title in quotes
        + r'(?:\s+"([^"]+)")?'  # Optional description in quotes
        + r"\)$"  # closing parenthesis
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown bookmark."""
        return text.strip().startswith("[bookmark]") and bool(
            cls.PATTERN.match(text.strip())
        )

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion bookmark."""
        return block.get("type") in ["bookmark", "external-bookmark"]

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown bookmark to Notion bookmark block."""
        bookmark_match = BookmarkElement.PATTERN.match(text.strip())
        if not bookmark_match:
            return None

        url = bookmark_match.group(1)
        title = bookmark_match.group(2)
        description = bookmark_match.group(3)

        bookmark_data = {"url": url}

        # Build caption string
        caption_parts = []
        if title:
            caption_parts.append(title)
        if description:
            caption_parts.append(description)

        if caption_parts:
            caption_text = " - ".join(caption_parts)
            caption_rich_text = RichTextObject.from_plain_text(caption_text)
            bookmark_data["caption"] = [caption_rich_text.model_dump()]
        else:
            bookmark_data["caption"] = []

        return [{"type": "bookmark", "bookmark": bookmark_data}]

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion bookmark block to markdown bookmark."""
        block_type = block.get("type", "")

        if block_type == "bookmark":
            bookmark_data = block.get("bookmark", {})
        elif block_type == "external-bookmark":
            url = block.get("url", "")
            if not url:
                return None

            return f"[bookmark]({url})"
        else:
            return None

        url = bookmark_data.get("url", "")

        if not url:
            return None

        caption = bookmark_data.get("caption", [])

        if not caption:
            # Simple bookmark with URL only
            return f"[bookmark]({url})"

        # Extract title and description from caption
        title, description = BookmarkElement._parse_caption(caption)

        if title and description:
            return f'[bookmark]({url} "{title}" "{description}")'

        if title:
            return f'[bookmark]({url} "{title}")'

        return f"[bookmark]({url})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Bookmarks are single-line elements."""
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
    def _parse_caption(cls, caption: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Parse Notion caption into title and description components.
        Returns a tuple of (title, description).
        """
        if not caption:
            return "", ""

        full_text = BookmarkElement._extract_text_content(caption)

        if " - " in full_text:
            parts = full_text.split(" - ", 1)
            return parts[0].strip(), parts[1].strip()

        return full_text.strip(), ""

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the bookmark element.
        """
        return (
            ElementPromptBuilder()
            .with_description("Creates a bookmark that links to an external website.")
            .with_usage_guidelines(
                "Use bookmarks when you want to reference external content while keeping the page clean and organized. "
                "Bookmarks display a preview card for the linked content."
            )
            .with_syntax(
                '[bookmark](https://example.com "Optional Title" "Optional Description")'
            )
            .with_examples(
                [
                    "[bookmark](https://example.com)",
                    '[bookmark](https://example.com "Example Title")',
                    '[bookmark](https://example.com "Example Title" "Example description of the site")',
                    '[bookmark](https://github.com "GitHub" "Where the world builds software")',
                ]
            )
            .build()
        )
