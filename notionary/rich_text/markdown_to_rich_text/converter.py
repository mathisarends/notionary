import re
from dataclasses import dataclass
from typing import ClassVar

from notionary.blocks.schemas import BlockColor
from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.matcher import PatternMatcher
from notionary.rich_text.schemas import RichText, RichTextType


@dataclass
class ColorGroup:
    color: BlockColor | None
    text: str


# TODO: Erstellen nur noch über factory
class MarkdownRichTextConverter:
    VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    def __init__(
        self, pattern_matcher: PatternMatcher, grammar: MarkdownGrammar
    ) -> None:
        self._pattern_matcher = pattern_matcher
        self._markdown_grammar = grammar

    async def to_rich_text(self, text: str) -> list[RichText]:
        if not text:
            return []

        color_groups = self._extract_color_groups(text)
        segments: list[RichText] = []

        for group in color_groups:
            group_segments = await self._parse_text_without_color(group.text)

            if group.color:
                group_segments = self._apply_color_to_segments(
                    group_segments, group.color
                )

            segments.extend(group_segments)

        return segments

    def _extract_color_groups(self, text: str) -> list[ColorGroup]:
        groups: list[ColorGroup] = []
        remaining_text = text

        bg_wrapper = self._markdown_grammar.background_color_wrapper
        valid_colors_pattern = "|".join(
            [c.replace("_background", "") for c in self.VALID_COLORS]
        )

        while remaining_text:
            fg_pattern = re.compile(
                rf"\(({valid_colors_pattern}):(.+?)\)", re.IGNORECASE
            )
            fg_match = fg_pattern.search(remaining_text)
            bg_pattern = re.compile(
                rf"{re.escape(bg_wrapper)}\{{({valid_colors_pattern})\}}(.+?){re.escape(bg_wrapper)}",
                re.IGNORECASE,
            )
            bg_match = bg_pattern.search(remaining_text)

            earliest_match = self._get_earliest_color_match(fg_match, bg_match)

            if not earliest_match:
                if remaining_text:
                    groups.append(ColorGroup(color=None, text=remaining_text))
                break

            match, is_background = earliest_match
            before_match = remaining_text[: match.start()]

            if before_match:
                groups.append(ColorGroup(color=None, text=before_match))

            color_name = match.group(1).lower()
            content = match.group(2)

            if is_background:
                color = BlockColor(f"{color_name}_background")
            else:
                color = BlockColor(color_name)
            groups.append(ColorGroup(color=color, text=content))

            remaining_text = remaining_text[match.end() :]

        return groups

    def _get_earliest_color_match(
        self, fg_match, bg_match
    ) -> tuple[re.Match, bool] | None:
        if fg_match and bg_match:
            if fg_match.start() < bg_match.start():
                return (fg_match, False)
            return (bg_match, True)
        elif fg_match:
            return (fg_match, False)
        elif bg_match:
            return (bg_match, True)
        return None

    async def _parse_text_without_color(self, text: str) -> list[RichText]:
        return await self._split_text_into_segments(text)

    def _apply_color_to_segments(
        self, segments: list[RichText], color: BlockColor
    ) -> list[RichText]:
        colored_segments = []
        for segment in segments:
            if segment.type == RichTextType.TEXT and segment.text:
                colored_segment = segment.model_copy(deep=True)
                if colored_segment.annotations:
                    colored_segment.annotations.color = color
                else:
                    from notionary.rich_text.schemas import TextAnnotations

                    colored_segment.annotations = TextAnnotations(color=color)
                colored_segments.append(colored_segment)
            else:
                colored_segments.append(segment)
        return colored_segments

    async def _split_text_into_segments(self, text: str) -> list[RichText]:
        segments: list[RichText] = []
        remaining_text = text

        while remaining_text:
            pattern_match = self._pattern_matcher.find_earliest_match(remaining_text)

            if not pattern_match:
                segments.append(RichText.from_plain_text(remaining_text))
                break

            plain_text_before = remaining_text[: pattern_match.position]
            if plain_text_before:
                segments.append(RichText.from_plain_text(plain_text_before))

            pattern_result = await self._pattern_matcher.process_match(pattern_match)
            self._add_pattern_result_to_segments(segments, pattern_result)

            remaining_text = remaining_text[pattern_match.end_position :]

        return segments

    def _add_pattern_result_to_segments(
        self, segments: list[RichText], pattern_result: RichText | list[RichText]
    ) -> None:
        if isinstance(pattern_result, list):
            segments.extend(pattern_result)
        elif pattern_result:
            segments.append(pattern_result)
