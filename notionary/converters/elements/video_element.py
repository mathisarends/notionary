import re
from typing import Dict, Any, Optional, List
from typing import override

from notionary.converters.notion_block_element import NotionBlockElement


class VideoElement(NotionBlockElement):
    """
    Handles conversion between Markdown video embeds and Notion video blocks.
    
    Markdown video syntax (custom format since standard Markdown doesn't support videos):
    - @[Caption](https://example.com/video.mp4) - Basic video with caption
    - @[](https://example.com/video.mp4) - Video without caption
    - @[Caption](https://example.com/video.mp4 "alt text") - Video with caption and alt text
    
    Supports various video URLs including YouTube, Vimeo, and direct video file links.
    """
    
    # Regex pattern for video syntax with optional alt text
    PATTERN = re.compile(
        r'^\@\[(.*?)\]' +                     # @[Caption] part
        r'\((https?://[^\s"]+)' +             # (URL part
        r'(?:\s+"([^"]+)")?' +                # Optional alt text in quotes
        r'\)$'                                 # closing parenthesis
    )
    
    # Supported video platforms and their domain patterns
    VIDEO_PLATFORMS = [
        'youtube.com', 'youtu.be',            # YouTube
        'vimeo.com',                          # Vimeo
        'dailymotion.com',                    # Dailymotion
        'twitch.tv',                          # Twitch
        'facebook.com',                       # Facebook
        'instagram.com'                       # Instagram
    ]
    
    # Video file extensions
    VIDEO_EXTENSIONS = ['.mp4', '.webm', '.mov', '.avi', '.wmv', '.flv', '.mkv']
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown video embed."""
        text = text.strip()
        if not text.startswith("@["):
            return False
        
        match = VideoElement.PATTERN.match(text)
        if not match:
            return False
            
        # Check if URL is a known video platform or has a video extension
        url = match.group(2).lower()
        is_video_platform = any(platform in url for platform in VideoElement.VIDEO_PLATFORMS)
        is_video_file = any(url.endswith(ext) for ext in VideoElement.VIDEO_EXTENSIONS)
        
        return is_video_platform or is_video_file
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion video."""
        return block.get("type") == "video"
    
    @override
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
            
        # Prepare the video block
        video_block = {
            "type": "video",
            "video": {
                "type": "external",
                "external": {
                    "url": url
                }
            }
        }
        
        # Add caption if provided
        if caption:
            video_block["video"]["caption"] = [
                {"type": "text", "text": {"content": caption}}
            ]
        
        return video_block
    
    @override
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
            
        # Extract caption if available
        caption = ""
        caption_rich_text = video_data.get("caption", [])
        if caption_rich_text:
            caption = VideoElement._extract_text_content(caption_rich_text)
            
        return f"@[{caption}]({url})"
    
    @override
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