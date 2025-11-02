import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from re import Match
from typing import ClassVar

from notionary.blocks.schemas import BlockColor
from notionary.rich_text.schemas import MentionType, RichText, RichTextType
from notionary.shared.name_id_resolver import (
    DatabaseNameIdResolver,
    DataSourceNameIdResolver,
    NameIdResolver,
    PageNameIdResolver,
    PersonNameIdResolver,
)


# TODO: Implement with ports https://claude.ai/chat/87e3ff77-d379-478a-aff2-01fd2cbf31b9
@dataclass
class PatternHandler(ABC):
    @property
    @abstractmethod
    def pattern(self) -> str:
        pass

    @abstractmethod
    async def handle(self, match: Match) -> RichText | list[RichText]:
        """Verarbeitet den Match und gibt RichText zurück."""

    @property
    def is_async(self) -> bool:
        """Standardmäßig async, kann überschrieben werden."""
        return True


# Einfache synchrone Formatter
class SyncFormatterHandler(PatternHandler):
    """Base class für synchrone, einfache Formatierungen."""

    @property
    def is_async(self) -> bool:
        return False

    async def handle(self, match: Match) -> RichText:
        # Async wrapper für sync Methode
        return self.handle_sync(match)

    @abstractmethod
    def handle_sync(self, match: Match) -> RichText:
        pass


class BoldHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"\*\*(.+?)\*\*"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), bold=True)


class ItalicHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"\*(.+?)\*"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), italic=True)


class ItalicUnderscoreHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"_([^_]+?)_"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), italic=True)


class UnderlineHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"__(.+?)__"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), underline=True)


class StrikethroughHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"~~(.+?)~~"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.from_plain_text(match.group(1), strikethrough=True)


class CodeHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"`(.+?)`"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.for_code_block(match.group(1))


class LinkHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"\[(.+?)\]\((.+?)\)"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.for_link(match.group(1), match.group(2))


class EquationHandler(SyncFormatterHandler):
    @property
    def pattern(self) -> str:
        return r"\$(.+?)\$"

    def handle_sync(self, match: Match) -> RichText:
        return RichText.equation_inline(match.group(1))


# Abstrakte Mention Handler Base Class
@dataclass
class MentionHandler(PatternHandler):
    """Base class für alle Mention-Handler mit gemeinsamer Logik."""

    resolver: NameIdResolver
    mention_type: MentionType

    @property
    @abstractmethod
    def mention_prefix(self) -> str:
        """Prefix für den Mention-Typ (z.B. 'page', 'user')."""
        pass

    @property
    def pattern(self) -> str:
        return rf"@{self.mention_prefix}\[([^\]]+)\]"

    @abstractmethod
    def create_mention(self, resolved_id: str) -> RichText:
        """Factory-Methode für spezifische Mention-Typen."""
        pass

    async def handle(self, match: Match) -> RichText:
        identifier = match.group(1)

        try:
            resolved_id = await self.resolver.resolve_name_to_id(identifier)

            if resolved_id:
                return self.create_mention(resolved_id)
            else:
                return self._create_fallback(identifier)

        except Exception:
            return self._create_fallback(identifier)

    def _create_fallback(self, identifier: str) -> RichText:
        fallback_text = f"@{self.mention_type.value}[{identifier}]"
        return RichText.for_caption(fallback_text)


class PageMentionHandler(MentionHandler):
    @property
    def mention_prefix(self) -> str:
        return "page"

    def create_mention(self, resolved_id: str) -> RichText:
        return RichText.mention_page(resolved_id)


class DatabaseMentionHandler(MentionHandler):
    @property
    def mention_prefix(self) -> str:
        return "database"

    def create_mention(self, resolved_id: str) -> RichText:
        return RichText.mention_database(resolved_id)


class DataSourceMentionHandler(MentionHandler):
    @property
    def mention_prefix(self) -> str:
        return "datasource"

    def create_mention(self, resolved_id: str) -> RichText:
        return RichText.mention_data_source(resolved_id)


class UserMentionHandler(MentionHandler):
    @property
    def mention_prefix(self) -> str:
        return "user"

    def create_mention(self, resolved_id: str) -> RichText:
        return RichText.mention_user(resolved_id)


# Color Handler (braucht Zugriff auf Converter für rekursives Parsing)
@dataclass
class ColorHandler(PatternHandler):
    """Handler für farbige Text-Segmente mit rekursivem Parsing."""

    converter: "MarkdownRichTextConverter"
    VALID_COLORS: ClassVar[set[str]] = {color.value for color in BlockColor}

    @property
    def pattern(self) -> str:
        return r"\((\w+):(.+?)\)"

    async def handle(self, match: Match) -> list[RichText]:
        color, content = match.group(1).lower(), match.group(2)

        if color not in self.VALID_COLORS:
            return [RichText.from_plain_text(f"({match.group(1)}:{content})")]

        # Rekursives Parsing des Inhalts
        parsed_segments = await self.converter._split_text_into_segments(content)

        return [self._apply_color(segment, color) for segment in parsed_segments]

    def _apply_color(self, segment: RichText, color: str) -> RichText:
        if segment.type != RichTextType.TEXT:
            return segment

        formatting = self._extract_formatting(segment.annotations)

        if segment.text and segment.text.link:
            return RichText.for_link(
                segment.plain_text, segment.text.link.url, color=color, **formatting
            )
        else:
            return RichText.from_plain_text(
                segment.plain_text, color=color, **formatting
            )

    def _extract_formatting(self, annotations) -> dict[str, bool]:
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


# Vereinfachter Converter
class MarkdownRichTextConverter:
    def __init__(
        self,
        *,
        page_resolver: NameIdResolver | None = None,
        database_resolver: NameIdResolver | None = None,
        data_source_resolver: NameIdResolver | None = None,
        person_resolver: NameIdResolver | None = None,
    ):
        # Resolvers mit Defaults
        self.page_resolver = page_resolver or PageNameIdResolver()
        self.database_resolver = database_resolver or DatabaseNameIdResolver()
        self.data_source_resolver = data_source_resolver or DataSourceNameIdResolver()
        self.person_resolver = person_resolver or PersonNameIdResolver()

        # Handler-Liste wird jetzt viel einfacher!
        self.handlers: list[PatternHandler] = [
            BoldHandler(),
            ItalicHandler(),
            ItalicUnderscoreHandler(),
            UnderlineHandler(),
            StrikethroughHandler(),
            CodeHandler(),
            LinkHandler(),
            EquationHandler(),
            ColorHandler(converter=self),  # Braucht Referenz für Rekursion
            PageMentionHandler(self.page_resolver, MentionType.PAGE),
            DatabaseMentionHandler(self.database_resolver, MentionType.DATABASE),
            DataSourceMentionHandler(self.data_source_resolver, MentionType.DATASOURCE),
            UserMentionHandler(self.person_resolver, MentionType.USER),
        ]

    async def to_rich_text(self, text: str) -> list[RichText]:
        if not text:
            return []
        return await self._split_text_into_segments(text)

    async def _split_text_into_segments(self, text: str) -> list[RichText]:
        segments: list[RichText] = []
        remaining_text = text

        while remaining_text:
            pattern_match = self._find_earliest_match(remaining_text)

            if not pattern_match:
                segments.append(RichText.from_plain_text(remaining_text))
                break

            handler, match = pattern_match

            # Plain text vor dem Match
            if match.start() > 0:
                segments.append(
                    RichText.from_plain_text(remaining_text[: match.start()])
                )

            # Pattern verarbeiten
            result = await handler.handle(match)

            if isinstance(result, list):
                segments.extend(result)
            else:
                segments.append(result)

            remaining_text = remaining_text[match.end() :]

        return segments

    def _find_earliest_match(self, text: str) -> tuple[PatternHandler, Match] | None:
        """Findet den frühesten Match aller Handler."""
        earliest_handler = None
        earliest_match = None
        earliest_pos = len(text)

        for handler in self.handlers:
            match = re.search(handler.pattern, text)
            if match and match.start() < earliest_pos:
                earliest_handler = handler
                earliest_match = match
                earliest_pos = match.start()

        return (earliest_handler, earliest_match) if earliest_handler else None
