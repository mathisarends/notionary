from typing import Optional
import re

# TODO: Use this inline formatting here
from notionary.blocks.models import (
    MentionRichText,
    RichTextObject,
    TextAnnotations,
    TextContent,
)

FORMAT_PATTERNS = [
    (r"\*\*(.+?)\*\*", {"bold": True}),
    (r"\*(.+?)\*", {"italic": True}),
    (r"_(.+?)_", {"italic": True}),
    (r"__(.+?)__", {"underline": True}),
    (r"~~(.+?)~~", {"strikethrough": True}),
    (r"`(.+?)`", {"code": True}),
    (r"\[(.+?)\]\((.+?)\)", {"link": True}),
    (r"@\[([0-9a-f-]+)\]", {"mention": True}),
]


def parse_inline_formatting(text: str) -> list[dict[str, any]]:
    """Parse inline text formatting into Notion rich_text format."""
    if not text:
        return []

    return _split_text_into_segments(text)


def _split_text_into_segments(text: str) -> list[dict[str, any]]:
    """Split text into segments by formatting markers."""
    segments = []
    remaining_text = text

    while remaining_text:
        match_info = _find_earliest_match(remaining_text)

        # No more formatting found - add remaining text and exit
        if not match_info:
            segments.append(_create_plain_text(remaining_text))
            break

        match, formatting, pos = match_info

        # Add text before match if exists
        if pos > 0:
            segments.append(_create_plain_text(remaining_text[:pos]))

        # Add formatted segment
        segments.append(_create_formatted_segment(match, formatting))

        # Update remaining text
        remaining_text = remaining_text[pos + len(match.group(0)) :]

    return segments


def _find_earliest_match(text: str) -> Optional[tuple]:
    """Find the earliest formatting match in text."""
    earliest_match = None
    earliest_format = None
    earliest_pos = len(text)

    for pattern, formatting in FORMAT_PATTERNS:
        match = re.search(pattern, text)
        if match and match.start() < earliest_pos:
            earliest_match = match
            earliest_format = formatting
            earliest_pos = match.start()

    return (earliest_match, earliest_format, earliest_pos) if earliest_match else None


def _create_formatted_segment(match: re.Match, formatting: dict) -> dict[str, any]:
    """Create a formatted segment based on match and formatting."""
    if "link" in formatting:
        return _create_link_text(match.group(1), match.group(2))
    elif "mention" in formatting:
        return _create_mention_text(match.group(1))
    else:
        return _create_formatted_text(match.group(1), **formatting)


def _create_plain_text(content: str) -> dict[str, any]:
    """Create plain text rich text object."""
    return RichTextObject.from_plain_text(content).model_dump()


def _create_formatted_text(content: str, **formatting) -> dict[str, any]:
    """Create formatted text rich text object."""
    return RichTextObject.from_plain_text(content, **formatting).model_dump()


def _create_link_text(content: str, url: str) -> dict[str, any]:
    """Create link text rich text object."""
    text_content = TextContent(content=content, link=url)
    annotations = TextAnnotations()

    rich_text = RichTextObject(
        text=text_content, annotations=annotations, plain_text=content, href=url
    )
    return rich_text.model_dump()


def _create_mention_text(page_id: str) -> dict[str, any]:
    """Create mention rich text object."""
    return MentionRichText.from_page_id(page_id).model_dump()


def extract_text_with_formatting(rich_text: list[dict[str, any]]) -> str:
    """Convert Notion rich_text elements back to Markdown."""
    return "".join(_rich_text_to_markdown(item) for item in rich_text)


def _rich_text_to_markdown(text_obj: dict[str, any]) -> str:
    """Convert single rich text object to markdown."""
    content = text_obj.get("plain_text", text_obj.get("text", {}).get("content", ""))
    annotations = text_obj.get("annotations", {})

    # Apply formatting in reverse order
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

    # Handle links
    link_data = text_obj.get("text", {}).get("link")
    if link_data and link_data.get("url"):
        content = f"[{content}]({link_data['url']})"

    return content
