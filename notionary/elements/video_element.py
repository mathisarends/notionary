import re
from typing import Dict, Any, Optional, List
from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class VideoElement(NotionBlockElement):
    """
    Handles conversion between Markdown video embeds and Notion video blocks.

    Markdown video syntax (custom format since standard Markdown doesn't support videos):
    - @[Caption](https://example.com/video.mp4) - Basic video with caption
    - @[](https://example.com/video.mp4) - Video without caption
    - @[Caption](https://www.youtube.com/watch?v=dQw4w9WgXcQ) - YouTube video
    - @[Caption](https://youtu.be/dQw4w9WgXcQ) - YouTube shortened URL

    Supports various video URLs including YouTube, Vimeo, and direct video file links.
    """

    PATTERN = re.compile(
        r"^\@\[(.*?)\]"  # @[Caption] part
        + r'\((https?://[^\s"]+)'  # (URL part
        + r"\)$"  # closing parenthesis
    )

    YOUTUBE_PATTERNS = [
        re.compile(
            r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})"
        ),
        re.compile(r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})"),
    ]

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown video embed."""
        text = text.strip()
        return text.startswith("@[") and bool(VideoElement.PATTERN.match(text))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion video."""
        return block.get("type") == "video"

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """Check if URL is a YouTube video and return video ID if it is."""
        for pattern in VideoElement.YOUTUBE_PATTERNS:
            match = pattern.match(url)
            if match:
                return True
        return False

    @staticmethod
    def get_youtube_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        for pattern in VideoElement.YOUTUBE_PATTERNS:
            match = pattern.match(url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown video embed to Notion video block."""
        video_match = VideoElement.PATTERN.match(text.strip())
        if not video_match:
            return None

        caption = video_match.group(1)
        url = video_match.group(2)

        if not url:
            return None

        youtube_id = VideoElement.get_youtube_id(url)
        if youtube_id:
            url = f"https://www.youtube.com/watch?v={youtube_id}"

        video_block = {
            "type": "video",
            "video": {"type": "external", "external": {"url": url}},
        }

        if caption:
            video_block["video"]["caption"] = [
                {"type": "text", "text": {"content": caption}}
            ]

        return video_block

    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion video block to markdown video embed."""
        if block.get("type") != "video":
            return None

        video_data = block.get("video", {})

        # Handle both external and file (uploaded) videos
        if video_data.get("type") == "external":
            url = video_data.get("external", {}).get("url", "")
        elif video_data.get("type") == "file":
            url = video_data.get("file", {}).get("url", "")
        else:
            return None

        if not url:
            return None

        caption = ""
        caption_rich_text = video_data.get("caption", [])
        if caption_rich_text:
            caption = VideoElement._extract_text_content(caption_rich_text)

        return f"@[{caption}]({url})"

    @staticmethod
    def is_multiline() -> bool:
        """Videos are single-line elements."""
        return False

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

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the video element.
        """
        return {
            "description": "Embeds video content from external sources like YouTube or direct video URLs.",
            "when_to_use": (
                "Use video embeds when you want to include multimedia content directly in your document. "
                "Videos are useful for tutorials, demonstrations, presentations, or any content that benefits from visual explanation."
            ),
            "syntax": "@[Caption](https://example.com/video.mp4)",
            "examples": [
                "@[How to use this feature](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                "@[Product demo](https://example.com/videos/demo.mp4)",
                "@[](https://youtu.be/dQw4w9WgXcQ)",
            ],
        }
