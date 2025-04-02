# File: converters/text_formatting.py

from typing import List, Dict, Any, Tuple
import re

def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
    """
    Parse inline text formatting (bold, italic, code, links, etc.) into Notion rich_text format.
    
    Args:
        text: Markdown text with inline formatting
        
    Returns:
        List of Notion rich_text objects
    """
    if not text:
        return []

    format_patterns = [
        (r'\*\*(.+?)\*\*', {'bold': True}),
        (r'\*(.+?)\*', {'italic': True}),
        (r'_(.+?)_', {'italic': True}),
        (r'__(.+?)__', {'underline': True}),
        (r'~~(.+?)~~', {'strikethrough': True}),
        (r'`(.+?)`', {'code': True}),
        (r'\[(.+?)\]\((.+?)\)', {'link': True}),
        (r'==([a-z_]+):(.+?)==', {'highlight': True}),
        (r'==(.+?)==', {'highlight_default': True}),
    ]
    
    return _split_text_into_segments(text, format_patterns)

def _split_text_into_segments(text: str, format_patterns: List[Tuple]) -> List[Dict[str, Any]]:
    """
    Split text into segments by formatting markers and convert to Notion rich_text format.
    
    Args:
        text: Text to split
        format_patterns: List of (regex pattern, formatting dict) tuples
        
    Returns:
        List of Notion rich_text objects
    """
    segments = []
    remaining_text = text
    
    while remaining_text:
        earliest_match = None
        earliest_format = None
        earliest_pos = len(remaining_text)
        
        # Find the earliest formatting marker
        for pattern, formatting in format_patterns:
            match = re.search(pattern, remaining_text)
            if match and match.start() < earliest_pos:
                earliest_match = match
                earliest_format = formatting
                earliest_pos = match.start()
        
        if earliest_match is None:
            if remaining_text:
                segments.append(_create_text_element(remaining_text, {}))
            break
        
        if earliest_pos > 0:
            segments.append(_create_text_element(remaining_text[:earliest_pos], {}))
        
        if 'highlight' in earliest_format:
            color = earliest_match.group(1)
            content = earliest_match.group(2)
            
            valid_colors = [
                "default", "gray", "brown", "orange", "yellow", "green", "blue", 
                "purple", "pink", "red", "gray_background", "brown_background", 
                "orange_background", "yellow_background", "green_background", 
                "blue_background", "purple_background", "pink_background", "red_background"
            ]
            
            if color not in valid_colors:
                if not color.endswith("_background"):
                    color = f"{color}_background"
                
                if color not in valid_colors:
                    color = "yellow_background"
            
            segments.append(_create_text_element(content, {'color': color}))
        
        elif 'highlight_default' in earliest_format:
            content = earliest_match.group(1)
            segments.append(_create_text_element(content, {'color': 'yellow_background'}))
        
        elif 'link' in earliest_format:
            content = earliest_match.group(1)
            url = earliest_match.group(2)
            segments.append(_create_link_element(content, url))
        
        else:
            content = earliest_match.group(1)
            segments.append(_create_text_element(content, earliest_format))
        
        # Move past the processed segment
        remaining_text = remaining_text[earliest_pos + len(earliest_match.group(0)):]
        
    return segments

def _create_text_element(text: str, formatting: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a Notion text element with formatting.
    """
    annotations = default_annotations()
    
    # Apply formatting
    for key, value in formatting.items():
        if key == 'color':
            annotations['color'] = value
        elif key in annotations:
            annotations[key] = value
    
    return {
        "type": "text",
        "text": {"content": text},
        "annotations": annotations,
        "plain_text": text
    }

def _create_link_element(text: str, url: str) -> Dict[str, Any]:
    """
    Create a Notion link element.
    
    Args:
        text: The link text
        url: The URL
        
    Returns:
        Notion rich_text element with link
    """
    return {
        "type": "text",
        "text": {
            "content": text,
            "link": {"url": url}
        },
        "annotations": default_annotations(),
        "plain_text": text
    }

def extract_text_with_formatting(rich_text: List[Dict[str, Any]]) -> str:
    """
    Extract text with Markdown formatting from Notion rich_text format.
    
    Args:
        rich_text: List of rich_text objects from Notion API
        
    Returns:
        Formatted text in Markdown
    """
    formatted_parts = []
    
    for text_obj in rich_text:
        content = text_obj.get("plain_text", "")
        annotations = text_obj.get("annotations", {})
        
        # Apply formatting based on annotations in reverse order to avoid conflicts
        # (e.g., bold inside italic)
        if annotations.get("code", False):
            content = f"`{content}`"
        if annotations.get("strikethrough", False):
            content = f"~~{content}~~"
        if annotations.get("underline", False):
            content = f"__{content}__"
        if annotations.get("italic", False):
            content = f"*{content}*"
        if annotations.get("bold", False):
            content = f"**{content}**"
        
        # Handle colored text
        color = annotations.get("color", "default")
        if color != "default":
            content = f"=={color.replace('_background', '')}:{content}=="
        
        # Handle links
        text_data = text_obj.get("text", {})
        link_data = text_data.get("link")
        if link_data:
            url = link_data.get("url", "")
            content = f"[{content}]({url})"
        
        formatted_parts.append(content)
    
    return "".join(formatted_parts)

def default_annotations() -> Dict[str, bool]:
    """
    Create default annotations object.
    
    Returns:
        Default Notion text annotations
    """
    return {
        "bold": False,
        "italic": False,
        "strikethrough": False,
        "underline": False,
        "code": False,
        "color": "default"
    }