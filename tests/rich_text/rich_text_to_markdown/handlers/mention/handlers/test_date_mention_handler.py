import pytest

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handlers.date import (
    DateMentionHandler,
)
from notionary.rich_text.schemas import DateMention, MentionDate


@pytest.fixture
def handler() -> DateMentionHandler:
    return DateMentionHandler(MarkdownGrammar())


@pytest.fixture
def expected_mention(markdown_grammar: MarkdownGrammar):
    def _format(date_range: str) -> str:
        return (
            f"{markdown_grammar.date_mention_prefix}"
            f"{date_range}"
            f"{markdown_grammar.mention_suffix}"
        )

    return _format


class TestDateMentionHandlerBasics:
    @pytest.mark.asyncio
    async def test_simple_date_mention(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15")

    @pytest.mark.asyncio
    async def test_date_mention_none(self, handler: DateMentionHandler) -> None:
        mention = DateMention(date=None)
        result = await handler.handle(mention)
        assert result == ""

    @pytest.mark.asyncio
    async def test_date_range_mention(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15", end="2024-01-20"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15–2024-01-20")


class TestDateMentionHandlerDateFormats:
    @pytest.mark.asyncio
    async def test_date_with_time(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15T14:30:00"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15T14:30:00")

    @pytest.mark.asyncio
    async def test_date_with_timezone(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(
            date=MentionDate(start="2024-01-15T14:30:00Z", time_zone="UTC")
        )

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15T14:30:00Z")

    @pytest.mark.asyncio
    async def test_date_range_with_times(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(
            date=MentionDate(start="2024-01-15T09:00:00", end="2024-01-15T17:00:00")
        )

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15T09:00:00–2024-01-15T17:00:00")

    @pytest.mark.asyncio
    async def test_datetime_with_offset(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15T14:30:00+02:00"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15T14:30:00+02:00")


class TestDateMentionHandlerDateRanges:
    @pytest.mark.asyncio
    async def test_single_day_range(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15", end="2024-01-15"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15–2024-01-15")

    @pytest.mark.asyncio
    async def test_week_range(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15", end="2024-01-21"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15–2024-01-21")

    @pytest.mark.asyncio
    async def test_month_range(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-01", end="2024-01-31"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-01–2024-01-31")

    @pytest.mark.asyncio
    async def test_year_range(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-01", end="2024-12-31"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-01–2024-12-31")

    @pytest.mark.asyncio
    async def test_cross_year_range(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2023-12-15", end="2024-01-15"))

        result = await handler.handle(mention)

        assert result == expected_mention("2023-12-15–2024-01-15")


class TestDateMentionHandlerEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_start_date(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start=""))

        result = await handler.handle(mention)

        assert result == expected_mention("")

    @pytest.mark.asyncio
    async def test_date_with_milliseconds(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15T14:30:00.123Z"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-15T14:30:00.123Z")

    @pytest.mark.asyncio
    async def test_historical_date(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="1900-01-01"))

        result = await handler.handle(mention)

        assert result == expected_mention("1900-01-01")

    @pytest.mark.asyncio
    async def test_future_date(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2099-12-31"))

        result = await handler.handle(mention)

        assert result == expected_mention("2099-12-31")


class TestDateMentionHandlerGrammarConsistency:
    @pytest.mark.asyncio
    async def test_uses_grammar_prefix_and_suffix(
        self, handler: DateMentionHandler, markdown_grammar: MarkdownGrammar
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15"))

        result = await handler.handle(mention)

        expected = (
            f"{markdown_grammar.date_mention_prefix}"
            f"2024-01-15"
            f"{markdown_grammar.mention_suffix}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_uses_en_dash_for_range(self, handler: DateMentionHandler) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-15", end="2024-01-20"))

        result = await handler.handle(mention)

        assert "–" in result
        assert "-" in result

    @pytest.mark.asyncio
    async def test_grammar_prefix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.date_mention_prefix == "@date["

    @pytest.mark.asyncio
    async def test_grammar_suffix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.mention_suffix == "]"


class TestDateMentionHandlerRealWorldExamples:
    @pytest.mark.asyncio
    async def test_meeting_date(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-03-15T10:00:00"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-03-15T10:00:00")

    @pytest.mark.asyncio
    async def test_project_deadline(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-12-31"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-12-31")

    @pytest.mark.asyncio
    async def test_vacation_period(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-07-01", end="2024-07-14"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-07-01–2024-07-14")

    @pytest.mark.asyncio
    async def test_conference_datetime(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(
            date=MentionDate(start="2024-11-05T09:00:00", end="2024-11-05T17:00:00")
        )

        result = await handler.handle(mention)

        assert result == expected_mention("2024-11-05T09:00:00–2024-11-05T17:00:00")

    @pytest.mark.asyncio
    async def test_birthday(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="1990-05-15"))

        result = await handler.handle(mention)

        assert result == expected_mention("1990-05-15")

    @pytest.mark.asyncio
    async def test_quarter_range(
        self, handler: DateMentionHandler, expected_mention
    ) -> None:
        mention = DateMention(date=MentionDate(start="2024-01-01", end="2024-03-31"))

        result = await handler.handle(mention)

        assert result == expected_mention("2024-01-01–2024-03-31")
