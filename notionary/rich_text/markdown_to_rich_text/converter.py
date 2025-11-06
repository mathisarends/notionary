from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.markdown_to_rich_text.handlers.factory import (
    create_pattern_handler_registry,
)
from notionary.rich_text.schemas import RichText
from notionary.shared.name_id_resolver import (
    DatabaseNameIdResolver,
    DataSourceNameIdResolver,
    NameIdResolver,
    PageNameIdResolver,
    PersonNameIdResolver,
)


class MarkdownRichTextConverter:
    def __init__(
        self,
        *,
        page_resolver: NameIdResolver | None = None,
        database_resolver: NameIdResolver | None = None,
        data_source_resolver: NameIdResolver | None = None,
        person_resolver: NameIdResolver | None = None,
        markdown_grammar: MarkdownGrammar | None = None,
    ):
        self.page_resolver = page_resolver or PageNameIdResolver()
        self.database_resolver = database_resolver or DatabaseNameIdResolver()
        self.data_source_resolver = data_source_resolver or DataSourceNameIdResolver()
        self.person_resolver = person_resolver or PersonNameIdResolver()
        self.markdown_grammar = markdown_grammar or MarkdownGrammar()

        self._handler_registry = create_pattern_handler_registry(
            page_resolver=self.page_resolver,
            database_resolver=self.database_resolver,
            data_source_resolver=self.data_source_resolver,
            person_resolver=self.person_resolver,
            grammar=self.markdown_grammar,
            converter=self,
        )

    async def to_rich_text(self, text: str) -> list[RichText]:
        if not text:
            return []
        return await self._split_text_into_segments(text)

    async def _split_text_into_segments(self, text: str) -> list[RichText]:
        segments: list[RichText] = []
        remaining_text = text

        while remaining_text:
            pattern_match = self._handler_registry.find_earliest_match(remaining_text)

            if not pattern_match:
                segments.append(RichText.from_plain_text(remaining_text))
                break

            plain_text_before = remaining_text[: pattern_match.position]
            if plain_text_before:
                segments.append(RichText.from_plain_text(plain_text_before))

            pattern_result = await self._handler_registry.process_match(pattern_match)
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
