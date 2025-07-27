import re
from typing import Dict, Any, Optional, List

from notionary.blocks import (
    ElementPromptContent,
    ElementPromptBuilder,
    NotionBlockResult,
    NotionBlockElement,
)


class VideoElement(NotionBlockElement):
    """
    Handles conversion between Markdown video embeds and Notion video blocks.

    Markdown video syntax:
    - [video](https://example.com/video.mp4) - Simple video with URL only
    - [video](https://example.com/video.mp4 "Caption") - Video with URL and caption

    Where:
    - URL is the required video URL
    - Caption is an optional descriptive text (enclosed in quotes)

    Supports various video URLs including YouTube, Vimeo, and direct video file links.
    """

    # Regex pattern for video syntax with optional caption
    PATTERN = re.compile(
        r"^\[video\]\("  # [video]( prefix
        + r'(https?://[^\s"]+)'  # URL (required)
        + r'(?:\s+"([^"]+)")?'  # Optional caption in quotes
        + r"\)$"  # closing parenthesis
    )

    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        re.compile(
            r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})"
        ),
        re.compile(r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})"),
    ]

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown video embed."""
        return text.strip().startswith("[video]") and bool(
            VideoElement.PATTERN.match(text.strip())
        )

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion video."""
        return block.get("type") == "video"

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown video embed to Notion video block."""
        video_match = VideoElement.PATTERN.match(text.strip())
        if not video_match:
            return None

        url = video_match.group(1)
        caption = video_match.group(2)

        if not url:
            return None

        # Normalize YouTube URLs
        youtube_id = VideoElement._get_youtube_id(url)
        if youtube_id:
            url = f"https://www.youtube.com/watch?v={youtube_id}"

        video_data = {"type": "external", "external": {"url": url}}

        # Add caption if provided
        if caption:
            video_data["caption"] = [{"type": "text", "text": {"content": caption}}]
        else:
            video_data["caption"] = []

        # Prepare the video block
        video_block = {"type": "video", "video": video_data}

        # Add empty paragraph after video
        empty_paragraph = {"type": "paragraph", "paragraph": {"rich_text": []}}

        return [video_block, empty_paragraph]

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion video block to markdown video embed."""
        if block.get("type") != "video":
            return None

        video_data = block.get("video", {})

        # Extract URL from video data
        url = VideoElement._extract_video_url(video_data)
        if not url:
            return None

        caption_rich_text = video_data.get("caption", [])

        if not caption_rich_text:
            # Simple video with URL only
            return f"[video]({url})"

        # Extract caption text
        caption = VideoElement._extract_text_content(caption_rich_text)

        if caption:
            return f'[video]({url} "{caption}")'

        return f"[video]({url})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Videos are single-line elements."""
        return False

    @classmethod
    def _is_youtube_url(cls, url: str) -> bool:
        """Check if URL is a YouTube video."""
        for pattern in VideoElement.YOUTUBE_PATTERNS:
            if pattern.match(url):
                return True
        return False

    @classmethod
    def _get_youtube_id(cls, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        for pattern in VideoElement.YOUTUBE_PATTERNS:
            match = pattern.match(url)
            if match:
                return match.group(1)
        return None

    @classmethod
    def _extract_video_url(cls, video_data: Dict[str, Any]) -> str:
        """Extract URL from video data, handling both external and uploaded videos."""
        if video_data.get("type") == "external":
            return video_data.get("external", {}).get("url", "")
        elif video_data.get("type") == "file":
            return video_data.get("file", {}).get("url", "")
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
        Returns structured LLM prompt metadata for the video element.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds video content from external sources like YouTube or direct video URLs."
            )
            .with_usage_guidelines(
                "Use video embeds when you want to include multimedia content directly in your document. "
                "Videos are useful for tutorials, demonstrations, presentations, or any content that benefits from visual explanation."
            )
            .with_syntax('[video](https://example.com/video.mp4 "Optional caption")')
            .with_examples(
                [
                    "[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                    '[video](https://example.com/videos/demo.mp4 "Product demo")',
                    '[video](https://youtu.be/dQw4w9WgXcQ "How to use this feature")',
                    '[video](https://example.com/tutorial.mp4 "Step-by-step tutorial")',
                ]
            )
            .build()
        )
