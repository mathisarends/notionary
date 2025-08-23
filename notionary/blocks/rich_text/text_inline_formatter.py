import re
from typing import Optional, Match

from notionary.blocks.rich_text.rich_text_models import (
    RichTextObject,
    RichTextType,
    MentionType,
    TemplateMentionType,
)
from notionary.blocks.types import BlockColor


class TextInlineFormatter:
    """
    Supported syntax patterns:

    • Bold
        **bold text**
        → RichTextObject(plain_text="bold text", bold=True)

    • Italic
        *italic text*   or   _italic text_
        → RichTextObject(plain_text="italic text", italic=True)

    • Underline
        __underlined text__
        → RichTextObject(plain_text="underlined text", underline=True)

    • Strikethrough
        ~~strikethrough~~
        → RichTextObject(plain_text="strikethrough", strikethrough=True)

    • Inline code
        `code snippet`
        → RichTextObject(plain_text="code snippet", code=True)

    • Link
        [link text](https://example.com)
        → RichTextObject.for_link("link text", "https://example.com")

    • Inline equation
        $E = mc^2$
        → RichTextObject.equation_inline("E = mc^2")

    • Colored text / highlight
        (red:important)            — sets text color to “red”
        (blue_background:note)     — sets background to “blue_background”
        → RichTextObject(plain_text="important", color="red")
        Valid colors are any value in the BlockColor enum, e.g.:
            default, gray, brown, orange, yellow, green, blue, purple, pink, red
        or their `_background` variants.

    • Page mention
        @page[123e4567-e89b-12d3-a456-426614174000]
        → RichTextObject.mention_page("123e4567-e89b-12d3-a456-426614174000")

    • Database mention
        @database[123e4567-e89b-12d3-a456-426614174000]
        → RichTextObject.mention_database("123e4567-e89b-12d3-a456-426614174000")
    """

    class Patterns:
        BOLD = r"\*\*(.+?)\*\*"
        ITALIC = r"\*(.+?)\*"
        ITALIC_UNDERSCORE = r"_([^_]+?)_"
        UNDERLINE = r"__(.+?)__"
        STRIKETHROUGH = r"~~(.+?)~~"
        CODE = r"`(.+?)`"
        LINK = r"\[(.+?)\]\((.+?)\)"
        INLINE_EQUATION = r"\$(.+?)\$"
        COLOR = r"\((\w+):(.+?)\)"  # (blue:colored text) or (blue_background:text)
        PAGE_MENTION = r"@page\[([0-9a-f-]+)\]"
        DATABASE_MENTION = r"@database\[([0-9a-f-]+)\]"

    # Pattern to handler mapping - cleaner approach
    @classmethod
    def _get_format_handlers(cls):
        """Get pattern to handler mapping - defined as method to access class methods."""
        return [
            (cls.Patterns.BOLD, cls._handle_bold_pattern),
            (cls.Patterns.ITALIC, cls._handle_italic_pattern),
            (cls.Patterns.ITALIC_UNDERSCORE, cls._handle_italic_pattern),
            (cls.Patterns.UNDERLINE, cls._handle_underline_pattern),
            (cls.Patterns.STRIKETHROUGH, cls._handle_strikethrough_pattern),
            (cls.Patterns.CODE, cls._handle_code_pattern),
            (cls.Patterns.LINK, cls._handle_link_pattern),
            (cls.Patterns.INLINE_EQUATION, cls._handle_equation_pattern),
            (cls.Patterns.COLOR, cls._handle_color_pattern),
            (cls.Patterns.PAGE_MENTION, cls._handle_page_mention_pattern),
            (cls.Patterns.DATABASE_MENTION, cls._handle_database_mention_pattern),
        ]

    # Valid Notion colors from BlockColor enum
    VALID_COLORS = {color.value for color in BlockColor}

    @classmethod
    def parse_inline_formatting(cls, text: str) -> list[RichTextObject]:
        """Main entry point: Parse markdown text into RichTextObjects."""
        if not text:
            return []
        return cls._split_text_into_segments(text)

    @classmethod
    def _split_text_into_segments(cls, text: str) -> list[RichTextObject]:
        """Core parsing logic - split text based on formatting patterns."""
        segments: list[RichTextObject] = []
        remaining = text

        while remaining:
            earliest_match = cls._find_earliest_pattern_match(remaining)

            if not earliest_match:
                # No more patterns - add remaining as plain text
                segments.append(RichTextObject.from_plain_text(remaining))
                break

            match, handler_name, position = earliest_match

            # Add any plain text before the pattern
            if position > 0:
                plain_text = remaining[:position]
                segments.append(RichTextObject.from_plain_text(plain_text))

            # Convert pattern to RichTextObject - direct handler call
            rich_text_obj = handler_name(match)
            if rich_text_obj:
                segments.append(rich_text_obj)

            # Continue with text after the pattern
            remaining = remaining[position + len(match.group(0)) :]

        return segments

    @classmethod
    def _find_earliest_pattern_match(
        cls, text: str
    ) -> Optional[tuple[Match, callable, int]]:
        """Find the pattern that appears earliest in the text."""
        earliest_match = None
        earliest_position = len(text)
        earliest_handler = None

        for pattern, handler_func in cls._get_format_handlers():
            match = re.search(pattern, text)
            if match and match.start() < earliest_position:
                earliest_match = match
                earliest_position = match.start()
                earliest_handler = handler_func

        if earliest_match:
            return earliest_match, earliest_handler, earliest_position
        return None

    @classmethod
    def _create_rich_text_from_pattern(
        cls, match: Match, handler_name: str
    ) -> Optional[RichTextObject]:
        """Create RichTextObject using existing factory methods for consistency."""

        # Dispatch to specific handler methods
        handlers = {
            "bold": cls._handle_bold_pattern,
            "italic": cls._handle_italic_pattern,
            "underline": cls._handle_underline_pattern,
            "strikethrough": cls._handle_strikethrough_pattern,
            "code": cls._handle_code_pattern,
            "link": cls._handle_link_pattern,
            "equation": cls._handle_equation_pattern,
            "color": cls._handle_color_pattern,
            "mention_page": cls._handle_page_mention_pattern,
        }

        handler = handlers.get(handler_name)
        if handler:
            return handler(match)

        return None

    # Pattern-specific handlers using existing RichTextObject factory methods

    @classmethod
    def _handle_bold_pattern(cls, match: Match) -> RichTextObject:
        return RichTextObject.from_plain_text(match.group(1), bold=True)

    @classmethod
    def _handle_italic_pattern(cls, match: Match) -> RichTextObject:
        return RichTextObject.from_plain_text(match.group(1), italic=True)

    @classmethod
    def _handle_underline_pattern(cls, match: Match) -> RichTextObject:
        return RichTextObject.from_plain_text(match.group(1), underline=True)

    @classmethod
    def _handle_strikethrough_pattern(cls, match: Match) -> RichTextObject:
        return RichTextObject.from_plain_text(match.group(1), strikethrough=True)

    @classmethod
    def _handle_code_pattern(cls, match: Match) -> RichTextObject:
        return RichTextObject.from_plain_text(match.group(1), code=True)

    @classmethod
    def _handle_link_pattern(cls, match: Match) -> RichTextObject:
        link_text, url = match.group(1), match.group(2)
        return RichTextObject.for_link(link_text, url)

    @classmethod
    def _handle_equation_pattern(cls, match: Match) -> RichTextObject:
        """Handle inline equations: $E = mc^2$"""
        expression = match.group(1)
        return RichTextObject.equation_inline(expression)

    @classmethod
    def _handle_color_pattern(cls, match: Match) -> RichTextObject:
        """Handle colored text: (blue:colored text) or (red_background:highlighted text)"""
        color, content = match.group(1).lower(), match.group(2)

        # Validate color against Notion's supported colors
        if color not in cls.VALID_COLORS:
            # Invalid color - return as plain text
            return RichTextObject.from_plain_text(f"({match.group(1)}:{content})")

        return RichTextObject.from_plain_text(content, color=color)

    @classmethod
    def _handle_page_mention_pattern(cls, match: Match) -> RichTextObject:
        """Handle page mentions: @page[page-id]"""
        page_id = match.group(1)
        return RichTextObject.mention_page(page_id)

    @classmethod
    def _handle_database_mention_pattern(cls, match: Match) -> RichTextObject:
        """Handle database mentions: @database[database-id]"""
        database_id = match.group(1)
        return RichTextObject.mention_database(database_id)

    @classmethod
    def extract_text_with_formatting(cls, rich_text: list[RichTextObject]) -> str:
        """Convert RichTextObjects back into markdown with inline formatting."""
        if not rich_text:
            return ""

        parts: list[str] = []

        for rich_obj in rich_text:
            formatted_text = cls._convert_rich_text_to_markdown(rich_obj)
            parts.append(formatted_text)

        return "".join(parts)

    @classmethod
    def _convert_rich_text_to_markdown(cls, obj: RichTextObject) -> str:
        """Convert single RichTextObject back to markdown format."""

        # Handle special types first
        if obj.type == RichTextType.EQUATION and obj.equation:
            return f"${obj.equation.expression}$"

        if obj.type == RichTextType.MENTION:
            mention_markdown = cls._extract_mention_markdown(obj)
            if mention_markdown:
                return mention_markdown

        # Handle regular text with formatting
        content = obj.plain_text or (obj.text.content if obj.text else "")
        return cls._apply_text_formatting_to_content(obj, content)

    @classmethod
    def _extract_mention_markdown(cls, obj: RichTextObject) -> Optional[str]:
        """Extract mention objects back to markdown format."""
        if not obj.mention:
            return None

        mention = obj.mention

        if mention.type == MentionType.PAGE and mention.page:
            return f"@page[{mention.page.id}]"

        if mention.type == MentionType.USER and mention.user:
            return f"@user({mention.user.id})"

        if mention.type == MentionType.DATABASE and mention.database:
            return f"@database[{mention.database.id}]"

        if mention.type == MentionType.DATE and mention.date:
            date_range = mention.date.start
            if mention.date.end:
                date_range += f"–{mention.date.end}"
            return date_range

        if mention.type == MentionType.TEMPLATE_MENTION and mention.template_mention:
            template_type = mention.template_mention.type
            return (
                "@template_user"
                if template_type == TemplateMentionType.USER
                else "@template_date"
            )

        if mention.type == MentionType.LINK_PREVIEW and mention.link_preview:
            return f"[{obj.plain_text}]({mention.link_preview.url})"

        return None

    @classmethod
    def _apply_text_formatting_to_content(
        cls, obj: RichTextObject, content: str
    ) -> str:
        """Apply text formatting annotations to content in correct order."""

        # Handle links first (they wrap the content)
        if obj.text and obj.text.link:
            content = f"[{content}]({obj.text.link.url})"

        # Apply formatting annotations if they exist
        if not obj.annotations:
            return content

        annotations = obj.annotations

        # Apply formatting in inside-out order
        if annotations.code:
            content = f"`{content}`"
        if annotations.strikethrough:
            content = f"~~{content}~~"
        if annotations.underline:
            content = f"__{content}__"
        if annotations.italic:
            content = f"*{content}*"
        if annotations.bold:
            content = f"**{content}**"

        # Handle colors (wrap everything)
        if annotations.color != "default" and annotations.color in cls.VALID_COLORS:
            content = f"({annotations.color}:{content})"

        return content
