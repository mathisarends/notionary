import re
from typing import Optional, Match, List

from notionary.blocks.rich_text.rich_text_models import (
    RichTextObject,
    RichTextType,
    MentionType,
    TemplateMentionType,
    MentionDate,
    MentionTemplateMention,
)
from notionary.blocks.types import BlockColor
from notionary.blocks.rich_text.name_to_id_resolver import NameIdResolver


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

    • Colored text / highlight (supports nested formatting)
        (red:important)                    — sets text color to "red"
        (blue_background:note)             — sets background to "blue_background"
        (red_background:**bold text**)     — red background with bold formatting
        → RichTextObject(plain_text="important", color="red", bold=True)
        Valid colors are any value in the BlockColor enum, e.g.:
            default, gray, brown, orange, yellow, green, blue, purple, pink, red
        or their `_background` variants.

    • Page mention
        @page[123e4567-e89b-12d3-a456-426614174000]  — by ID
        @page[Page Name]                             — by name
        → RichTextObject.mention_page("resolved-id")

    • Database mention
        @database[123e4567-e89b-12d3-a456-426614174000]  — by ID
        @database[Database Name]                         — by name
        → RichTextObject.mention_database("resolved-id")
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
        PAGE_MENTION = r"@page\[([^\]]+)\]"  # Matches both IDs and names
        DATABASE_MENTION = r"@database\[([^\]]+)\]"  # Matches both IDs and names
        USER_MENTION = r"@user\[([^\]]+)\]"  # Matches both IDs and names

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
            (cls.Patterns.USER_MENTION, cls._handle_user_mention_pattern),
        ]

    VALID_COLORS = {color.value for color in BlockColor}

    _resolver: Optional[NameIdResolver] = None

    @classmethod
    def set_resolver(cls, resolver: Optional[NameIdResolver]) -> None:
        """Set the name-to-ID resolver instance."""
        cls._resolver = resolver

    @classmethod
    def get_resolver(cls) -> NameIdResolver:
        """Get or create the name-to-ID resolver instance."""
        if cls._resolver is None:
            cls._resolver = NameIdResolver()
        return cls._resolver

    @classmethod
    async def parse_inline_formatting(cls, text: str) -> list[RichTextObject]:
        """Main entry point: Parse markdown text into RichTextObjects."""
        if not text:
            return []
        return await cls._split_text_into_segments(text)

    @classmethod
    async def _split_text_into_segments(cls, text: str) -> list[RichTextObject]:
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

            # Convert pattern to RichTextObject(s) - handlers can now return single objects or lists
            if handler_name in [
                cls._handle_page_mention_pattern,
                cls._handle_database_mention_pattern,
                cls._handle_user_mention_pattern,
                cls._handle_color_pattern,  # Color pattern also needs async for recursive parsing
            ]:
                result = await handler_name(match)
            else:
                result = handler_name(match)

            # Handle both single RichTextObject and list of RichTextObjects
            if isinstance(result, list):
                segments.extend(result)
            elif result:
                segments.append(result)

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
    async def _handle_color_pattern(cls, match: Match) -> List[RichTextObject]:
        """Handle colored text with support for nested formatting: (blue:**bold text**)"""
        color, content = match.group(1).lower(), match.group(2)

        if color not in cls.VALID_COLORS:
            return [RichTextObject.from_plain_text(f"({match.group(1)}:{content})")]

        # Recursively parse the content inside the color pattern for nested formatting
        parsed_segments = await cls._split_text_into_segments(content)

        # Apply the color to all resulting segments
        colored_segments = []
        for segment in parsed_segments:
            # Create a new RichTextObject with the same formatting but with the color applied
            if segment.type == RichTextType.TEXT:
                # For text segments, we can combine the color with existing formatting
                colored_segment = cls._apply_color_to_text_segment(segment, color)
                colored_segments.append(colored_segment)
            else:
                # For non-text segments (equations, mentions, etc.), keep as-is
                colored_segments.append(segment)

        return colored_segments

    @classmethod
    def _apply_color_to_text_segment(
        cls, segment: RichTextObject, color: str
    ) -> RichTextObject:
        """Apply color to a text segment while preserving existing formatting."""
        if segment.type != RichTextType.TEXT:
            return segment

        # Extract existing formatting
        annotations = segment.annotations
        text_content = segment.text
        plain_text = segment.plain_text

        # Create new RichTextObject with color and existing formatting
        if text_content and text_content.link:
            # For links, preserve the link while adding color and formatting
            return RichTextObject.for_link(
                plain_text,
                text_content.link.url,
                bold=annotations.bold if annotations else False,
                italic=annotations.italic if annotations else False,
                strikethrough=annotations.strikethrough if annotations else False,
                underline=annotations.underline if annotations else False,
                code=annotations.code if annotations else False,
                color=color,
            )
        else:
            # For regular text, combine all formatting
            return RichTextObject.from_plain_text(
                plain_text,
                bold=annotations.bold if annotations else False,
                italic=annotations.italic if annotations else False,
                strikethrough=annotations.strikethrough if annotations else False,
                underline=annotations.underline if annotations else False,
                code=annotations.code if annotations else False,
                color=color,
            )

    @classmethod
    async def _handle_page_mention_pattern(cls, match: Match) -> RichTextObject:
        """Handle page mentions: @page[page-id-or-name]"""
        page_identifier = match.group(1)

        resolver = cls.get_resolver()
        page_id = await resolver.resolve_page_id(page_identifier)

        if page_id:
            return RichTextObject.mention_page(page_id)
        else:
            # If resolution fails, treat as plain text
            return RichTextObject.for_caption(f"@page[{page_identifier}]")

    @classmethod
    async def _handle_database_mention_pattern(cls, match: Match) -> RichTextObject:
        """Handle database mentions: @database[database-id-or-name]"""
        database_identifier = match.group(1)

        resolver = cls.get_resolver()
        database_id = await resolver.resolve_database_id(database_identifier)

        if database_id:
            return RichTextObject.mention_database(database_id)
        else:
            # If resolution fails, treat as plain text
            return RichTextObject.for_caption(f"@database[{database_identifier}]")

    @classmethod
    async def _handle_user_mention_pattern(cls, match: Match) -> RichTextObject:
        """Handle user mentions: @user[user-id-or-name]"""
        user_identifier = match.group(1)

        resolver = cls.get_resolver()
        user_id = await resolver.resolve_user_id(user_identifier)

        if user_id:
            return RichTextObject.mention_user(user_id)
        else:
            # If resolution fails, treat as plain text
            return RichTextObject.for_caption(f"@user[{user_identifier}]")

    @classmethod
    async def extract_text_with_formatting(cls, rich_text: list[RichTextObject]) -> str:
        """Convert RichTextObjects back into markdown with inline formatting."""
        if not rich_text:
            return ""

        parts: list[str] = []

        for rich_obj in rich_text:
            formatted_text = await cls._convert_rich_text_to_markdown(rich_obj)
            parts.append(formatted_text)

        return "".join(parts)

    @classmethod
    async def _convert_rich_text_to_markdown(cls, obj: RichTextObject) -> str:
        """Convert single RichTextObject back to markdown format."""

        # Handle special types first
        if obj.type == RichTextType.EQUATION and obj.equation:
            return f"${obj.equation.expression}$"

        if obj.type == RichTextType.MENTION:
            mention_markdown = await cls._extract_mention_markdown(obj)
            if mention_markdown:
                return mention_markdown

        # Handle regular text with formatting
        content = obj.plain_text or (obj.text.content if obj.text else "")
        return cls._apply_text_formatting_to_content(obj, content)

    @classmethod
    async def _extract_mention_markdown(cls, obj: RichTextObject) -> Optional[str]:
        """Extract mention objects back to markdown format with human-readable names."""
        if not obj.mention:
            return None

        mention = obj.mention
        
        # Handle different mention types
        if mention.type == MentionType.PAGE and mention.page:
            return await cls._extract_page_mention_markdown(mention.page.id)
        
        if mention.type == MentionType.DATABASE and mention.database:
            return await cls._extract_database_mention_markdown(mention.database.id)
        
        if mention.type == MentionType.USER and mention.user:
            return await cls._extract_user_mention_markdown(mention.user.id)
        
        if mention.type == MentionType.DATE and mention.date:
            return cls._extract_date_mention_markdown(mention.date)
        
        if mention.type == MentionType.TEMPLATE_MENTION and mention.template_mention:
            return cls._extract_template_mention_markdown(mention.template_mention)
        
        if mention.type == MentionType.LINK_PREVIEW and mention.link_preview:
            return f"[{obj.plain_text}]({mention.link_preview.url})"

        return None

    @classmethod
    async def _extract_page_mention_markdown(cls, page_id: str) -> str:
        """Extract page mention to markdown format."""
        resolver = cls.get_resolver()
        page_name = await resolver.resolve_page_name(page_id)
        return f"@page[{page_name or page_id}]"

    @classmethod
    async def _extract_database_mention_markdown(cls, database_id: str) -> str:
        """Extract database mention to markdown format."""
        resolver = cls.get_resolver()
        database_name = await resolver.resolve_database_name(database_id)
        return f"@database[{database_name or database_id}]"

    @classmethod
    async def _extract_user_mention_markdown(cls, user_id: str) -> str:
        """Extract user mention to markdown format."""
        resolver = cls.get_resolver()
        user_name = await resolver.resolve_user_name(user_id)
        return f"@user[{user_name or user_id}]"

    @classmethod
    def _extract_date_mention_markdown(cls, date_mention: MentionDate) -> str:
        """Extract date mention to markdown format."""
        date_range = date_mention.start
        if date_mention.end:
            date_range += f"–{date_mention.end}"
        return date_range

    @classmethod
    def _extract_template_mention_markdown(cls, template_mention: MentionTemplateMention) -> str:
        """Extract template mention to markdown format."""
        template_type = template_mention.type
        return (
            "@template_user"
            if template_type == TemplateMentionType.USER
            else "@template_date"
        )

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
