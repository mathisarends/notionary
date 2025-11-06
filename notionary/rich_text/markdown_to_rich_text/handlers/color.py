"""Color pattern handler with recursive text parsing."""

from re import Match, Pattern
from typing import TYPE_CHECKING, ClassVar

from notionary.blocks.schemas import BlockColor
from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.schemas import RichText, RichTextType, TextAnnotations

if TYPE_CHECKING:
    from notionary.rich_text.markdown_to_rich_text.converter import (
        MarkdownRichTextConverter,
    )


class ColorPatternHandler(BasePatternHandler):
    VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    def __init__(
        self, grammar: MarkdownGrammar, converter: "MarkdownRichTextConverter"
    ) -> None:
        self._grammar = grammar
        self._converter = converter

    @property
    def pattern(self) -> Pattern:
        return self._grammar.color_pattern

    async def handle(self, match: Match) -> list[RichText]:
        color, content = match.group(1).lower(), match.group(2)

        if color not in self.VALID_COLORS:
            return [RichText.from_plain_text(f"({match.group(1)}:{content})")]

        parsed_segments = await self._converter._split_text_into_segments(content)

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
        return RichText.for_link(
            segment.plain_text, segment.text.link.url, color=color, **formatting
        )

    def _apply_color_to_plain_text_segment(
        self, segment: RichText, color: str
    ) -> RichText:
        formatting = self._extract_formatting_attributes(segment.annotations)
        return RichText.from_plain_text(segment.plain_text, color=color, **formatting)

    def _extract_formatting_attributes(
        self, annotations: TextAnnotations
    ) -> dict[str, bool]:
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
