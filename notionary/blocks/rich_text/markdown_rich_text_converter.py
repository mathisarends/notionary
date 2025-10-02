import re
from collections.abc import Callable
from dataclasses import dataclass
from re import Match
from typing import ClassVar

from notionary.blocks.rich_text.name_id_resolver.database_name_id_resolver import DatabaseNameIdResolver
from notionary.blocks.rich_text.name_id_resolver.name_id_resolver import NameIdResolver
from notionary.blocks.rich_text.name_id_resolver.page_name_id_resolver import PageNameIdResolver
from notionary.blocks.rich_text.name_id_resolver.person_name_id_resolver import PersonNameIdResolver
from notionary.blocks.rich_text.rich_text_models import MentionType, RichText, RichTextType, TextAnnotations
from notionary.blocks.rich_text.rich_text_patterns import RichTextPatterns
from notionary.blocks.types import BlockColor


@dataclass
class PatternMatch:
    match: Match
    handler: Callable[[Match], RichText | list[RichText]]
    position: int

    @property
    def matched_text(self) -> str:
        return self.match.group(0)

    @property
    def end_position(self) -> int:
        return self.position + len(self.matched_text)


@dataclass
class PatternHandler:
    pattern: str
    handler: Callable[[Match], RichText | list[RichText]]


class MarkdownRichTextConverter:
    VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    def __init__(
        self,
        *,
        page_resolver: NameIdResolver | None = None,
        database_resolver: NameIdResolver | None = None,
        person_resolver: NameIdResolver | None = None,
    ):
        self.page_resolver = page_resolver or PageNameIdResolver()
        self.database_resolver = database_resolver or DatabaseNameIdResolver()
        self.person_resolver = person_resolver or PersonNameIdResolver()
        self.format_handlers = self._setup_format_handlers()

    def _setup_format_handlers(self) -> list[PatternHandler]:
        return [
            PatternHandler(RichTextPatterns.BOLD, self._handle_bold_pattern),
            PatternHandler(RichTextPatterns.ITALIC, self._handle_italic_pattern),
            PatternHandler(RichTextPatterns.ITALIC_UNDERSCORE, self._handle_italic_pattern),
            PatternHandler(RichTextPatterns.UNDERLINE, self._handle_underline_pattern),
            PatternHandler(RichTextPatterns.STRIKETHROUGH, self._handle_strikethrough_pattern),
            PatternHandler(RichTextPatterns.CODE, self._handle_code_pattern),
            PatternHandler(RichTextPatterns.LINK, self._handle_link_pattern),
            PatternHandler(RichTextPatterns.INLINE_EQUATION, self._handle_equation_pattern),
            PatternHandler(RichTextPatterns.COLOR, self._handle_color_pattern),
            PatternHandler(RichTextPatterns.PAGE_MENTION, self._handle_page_mention_pattern),
            PatternHandler(RichTextPatterns.DATABASE_MENTION, self._handle_database_mention_pattern),
            PatternHandler(RichTextPatterns.USER_MENTION, self._handle_user_mention_pattern),
        ]

    async def to_rich_text(self, text: str) -> list[RichText]:
        if not text:
            return []
        return await self._split_text_into_segments(text)

    async def _split_text_into_segments(self, text: str) -> list[RichText]:
        segments: list[RichText] = []
        remaining_text = text

        while remaining_text:
            pattern_match = self._find_earliest_pattern_match(remaining_text)

            if not pattern_match:
                segments.append(RichText.from_plain_text(remaining_text))
                break

            plain_text_before = remaining_text[: pattern_match.position]
            if plain_text_before:
                segments.append(RichText.from_plain_text(plain_text_before))

            pattern_result = await self._process_pattern_match(pattern_match)
            self._add_pattern_result_to_segments(segments, pattern_result)

            remaining_text = remaining_text[pattern_match.end_position :]

        return segments

    def _find_earliest_pattern_match(self, text: str) -> PatternMatch | None:
        """Find the pattern that appears earliest in the text."""
        earliest_match = None
        earliest_position = len(text)

        for pattern_handler in self.format_handlers:
            match = re.search(pattern_handler.pattern, text)
            if match and match.start() < earliest_position:
                earliest_match = PatternMatch(match=match, handler=pattern_handler.handler, position=match.start())
                earliest_position = match.start()

        return earliest_match

    async def _process_pattern_match(self, pattern_match: PatternMatch) -> RichText | list[RichText]:
        handler_method = pattern_match.handler

        if self._is_async_handler(handler_method):
            return await handler_method(pattern_match.match)
        else:
            return handler_method(pattern_match.match)

    def _is_async_handler(self, handler_method: Callable) -> bool:
        async_handlers = {
            self._handle_page_mention_pattern,
            self._handle_database_mention_pattern,
            self._handle_color_pattern,  # Color pattern needs async for recursive parsing
            self._handle_user_mention_pattern,
        }
        return handler_method in async_handlers

    def _add_pattern_result_to_segments(
        self, segments: list[RichText], pattern_result: RichText | list[RichText]
    ) -> None:
        if isinstance(pattern_result, list):
            segments.extend(pattern_result)
        elif pattern_result:
            segments.append(pattern_result)

    async def _handle_color_pattern(self, match: Match) -> list[RichText]:
        color, content = match.group(1).lower(), match.group(2)

        if color not in self.VALID_COLORS:
            return [RichText.from_plain_text(f"({match.group(1)}:{content})")]

        parsed_segments = await self._split_text_into_segments(content)

        colored_segments = []
        for segment in parsed_segments:
            if segment.type == RichTextType.TEXT:
                colored_segment = self._apply_color_to_text_segment(segment, color)
                colored_segments.append(colored_segment)
            else:
                colored_segments.append(segment)

        return colored_segments

    def _apply_color_to_text_segment(self, segment: RichText, color: str) -> RichText:
        if segment.type != RichTextType.TEXT:
            return segment

        has_link = segment.text and segment.text.link

        if has_link:
            return self._apply_color_to_link_segment(segment, color)
        else:
            return self._apply_color_to_plain_text_segment(segment, color)

    def _apply_color_to_link_segment(self, segment: RichText, color: str) -> RichText:
        formatting = self._extract_formatting_attributes(segment.annotations)

        return RichText.for_link(segment.plain_text, segment.text.link.url, color=color, **formatting)

    def _apply_color_to_plain_text_segment(self, segment: RichText, color: str) -> RichText:
        if segment.type != RichTextType.TEXT:
            return segment

        formatting = self._extract_formatting_attributes(segment.annotations)

        return RichText.from_plain_text(segment.plain_text, color=color, **formatting)

    def _extract_formatting_attributes(self, annotations: TextAnnotations) -> dict[str, bool]:
        if not annotations:
            return {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
            }

        return {
            "bold": annotations.bold,
            "italic": annotations.italic,
            "strikethrough": annotations.strikethrough,
            "underline": annotations.underline,
            "code": annotations.code,
        }

    async def _handle_page_mention_pattern(self, match: Match) -> RichText:
        identifier = match.group(1)
        return await self._create_mention_or_fallback(
            identifier=identifier,
            resolve_func=self.page_resolver.resolve_name_to_id,
            create_mention_func=RichText.mention_page,
            mention_type=MentionType.PAGE,
        )

    async def _handle_database_mention_pattern(self, match: Match) -> RichText:
        identifier = match.group(1)
        return await self._create_mention_or_fallback(
            identifier=identifier,
            resolve_func=self.database_resolver.resolve_name_to_id,
            create_mention_func=RichText.mention_database,
            mention_type=MentionType.DATABASE,
        )

    async def _handle_user_mention_pattern(self, match: Match) -> RichText:
        identifier = match.group(1)
        return await self._create_mention_or_fallback(
            identifier=identifier,
            resolve_func=self.person_resolver.resolve_name_to_id,
            create_mention_func=RichText.mention_user,
            mention_type=MentionType.USER,
        )

    async def _create_mention_or_fallback(
        self,
        identifier: str,
        resolve_func: Callable[[str], str | None],
        create_mention_func: Callable[[str], RichText],
        mention_type: MentionType,
    ) -> RichText:
        try:
            resolved_id = await resolve_func(identifier)

            if resolved_id:
                return create_mention_func(resolved_id)
            else:
                return self._create_unresolved_mention_fallback(identifier, mention_type)

        except Exception:
            # If resolution throws an error, fallback to plain text
            return self._create_unresolved_mention_fallback(identifier, mention_type)

    def _create_unresolved_mention_fallback(self, identifier: str, mention_type: MentionType) -> RichText:
        fallback_text = f"@{mention_type.value}[{identifier}]"
        return RichText.for_caption(fallback_text)

    def _handle_bold_pattern(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), bold=True)

    def _handle_italic_pattern(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), italic=True)

    def _handle_underline_pattern(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), underline=True)

    def _handle_strikethrough_pattern(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), strikethrough=True)

    def _handle_code_pattern(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), code=True)

    def _handle_link_pattern(self, match: Match) -> RichText:
        link_text, url = match.group(1), match.group(2)
        return RichText.for_link(link_text, url)

    def _handle_equation_pattern(self, match: Match) -> RichText:
        expression = match.group(1)
        return RichText.equation_inline(expression)
