import re
from typing import Dict, Any, Optional, List
from typing_extensions import override
from notionary.elements.notion_block_element import NotionBlockElement


class ImageElement(NotionBlockElement):
    """
    Handles conversion between Markdown images and Notion image blocks.

    Markdown image syntax:
    - ![Caption](https://example.com/image.jpg) - Basic image with caption
    - ![](https://example.com/image.jpg) - Image without caption
    - ![Caption](https://example.com/image.jpg "alt text") - Image with caption and alt text
    """

    # Regex pattern for image syntax with optional alt text
    PATTERN = re.compile(
        r"^\!\[(.*?)\]"  # ![Caption] part
        + r'\((https?://[^\s"]+)'  # (URL part
        + r'(?:\s+"([^"]+)")?'  # Optional alt text in quotes
        + r"\)$"  # closing parenthesis
    )

    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown image."""
        return text.strip().startswith("![") and bool(
            ImageElement.PATTERN.match(text.strip())
        )

    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion image."""
        return block.get("type") == "image"

    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown image to Notion image block."""
        image_match = ImageElement.PATTERN.match(text.strip())
        if not image_match:
            return None

        caption = image_match.group(1)
        url = image_match.group(2)

        if not url:
            return None

        # Prepare the image block
        image_block = {
            "type": "image",
            "image": {"type": "external", "external": {"url": url}},
        }

        # Add caption if provided
        if caption:
            image_block["image"]["caption"] = [
                {"type": "text", "text": {"content": caption}}
            ]

        return image_block

    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion image block to markdown image."""
        if block.get("type") != "image":
            return None

        image_data = block.get("image", {})

        # Handle both external and file (uploaded) images
        if image_data.get("type") == "external":
            url = image_data.get("external", {}).get("url", "")
        elif image_data.get("type") == "file":
            url = image_data.get("file", {}).get("url", "")
        else:
            return None

        if not url:
            return None

        # Extract caption if available
        caption = ""
        caption_rich_text = image_data.get("caption", [])
        if caption_rich_text:
            caption = ImageElement._extract_text_content(caption_rich_text)

        return f"![{caption}]({url})"

    @staticmethod
    def _extract_text_content(rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result

    @override
    @staticmethod
    def is_multiline() -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> dict:
        """
        Returns a dictionary with all information needed for LLM prompts about this element.
        Includes description, usage guidance, syntax options, and examples.
        """
        return {
            "description": "Embeds an image from an external URL into your document.",
            "when_to_use": "Use images to include visual content such as diagrams, screenshots, charts, photos, or illustrations that enhance your document. Images can make complex information easier to understand, create visual interest, or provide evidence for your points.",
            "syntax": [
                "![](https://example.com/image.jpg) - Image without caption",
                "![Caption text](https://example.com/image.jpg) - Image with caption",
                '![Caption text](https://example.com/image.jpg "Alt text") - Image with caption and alt text',
            ],
            "examples": [
                "![Data visualization showing monthly trends](https://example.com/chart.png)",
                "![](https://example.com/screenshot.jpg)",
                '![Company logo](https://company.com/logo.png "Company Inc. logo")',
            ],
        }
