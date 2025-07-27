import re
from typing import Dict, Any, Optional, List

from notionary.blocks import NotionBlockElement
from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
)


class ImageElement(NotionBlockElement):
    """
    Handles conversion between Markdown images and Notion image blocks.

    Markdown image syntax:
    - [image](https://example.com/image.jpg) - Simple image with URL only
    - [image](https://example.com/image.jpg "Caption") - Image with URL and caption

    Where:
    - URL is the required image URL
    - Caption is an optional descriptive text (enclosed in quotes)
    """

    # Regex pattern for image syntax with optional caption
    PATTERN = re.compile(
        r"^\[image\]\("  # [image]( prefix
        + r'(https?://[^\s"]+)'  # URL (required)
        + r'(?:\s+"([^"]+)")?'  # Optional caption in quotes
        + r"\)$"  # closing parenthesis
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown image."""
        return text.strip().startswith("[image]") and bool(
            ImageElement.PATTERN.match(text.strip())
        )

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion image."""
        return block.get("type") == "image"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown image to Notion image block."""
        image_match = ImageElement.PATTERN.match(text.strip())
        if not image_match:
            return None

        url = image_match.group(1)
        caption = image_match.group(2)

        if not url:
            return None

        image_data = {"type": "external", "external": {"url": url}}

        # Add caption if provided
        if caption:
            image_data["caption"] = [{"type": "text", "text": {"content": caption}}]
        else:
            image_data["caption"] = []

        # Prepare the image block
        image_block = {"type": "image", "image": image_data}

        # Add empty paragraph after image
        empty_paragraph = {"type": "paragraph", "paragraph": {"rich_text": []}}

        return [image_block, empty_paragraph]

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion image block to markdown image."""
        if block.get("type") != "image":
            return None

        image_data = block.get("image", {})

        # Handle both external and file (uploaded) images
        url = ImageElement._extract_image_url(image_data)
        if not url:
            return None

        caption_rich_text = image_data.get("caption", [])

        if not caption_rich_text:
            # Simple image with URL only
            return f"[image]({url})"

        # Extract caption text
        caption = ImageElement._extract_text_content(caption_rich_text)

        if caption:
            return f'[image]({url} "{caption}")'

        return f"[image]({url})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Images are single-line elements."""
        return False

    @classmethod
    def _extract_image_url(cls, image_data: Dict[str, Any]) -> str:
        """Extract URL from image data, handling both external and uploaded images."""
        if image_data.get("type") == "external":
            return image_data.get("external", {}).get("url", "")
        elif image_data.get("type") == "file":
            return image_data.get("file", {}).get("url", "")
        return ""

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
        Returns structured LLM prompt metadata for the image element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds an image from an external URL into your document."
            )
            .with_usage_guidelines(
                "Use images to include visual content such as diagrams, screenshots, charts, photos, or illustrations "
                "that enhance your document. Images can make complex information easier to understand, create visual interest, "
                "or provide evidence for your points."
            )
            .with_syntax('[image](https://example.com/image.jpg "Optional caption")')
            .with_examples(
                [
                    "[image](https://example.com/chart.png)",
                    '[image](https://example.com/screenshot.jpg "Data visualization showing monthly trends")',
                    '[image](https://company.com/logo.png "Company Inc. logo")',
                    '[image](https://example.com/diagram.jpg "System architecture overview")',
                ]
            )
            .build()
        )
