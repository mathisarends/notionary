from unittest.mock import AsyncMock

import pytest

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handlers.data_source import (
    DataSourceMentionHandler,
)
from notionary.rich_text.schemas import DataSourceMention, MentionDataSourceRef


@pytest.fixture
def mock_data_source_resolver():
    resolver = AsyncMock()
    resolver.resolve_id_to_name = AsyncMock()
    return resolver


@pytest.fixture
def handler(mock_data_source_resolver) -> DataSourceMentionHandler:
    return DataSourceMentionHandler(MarkdownGrammar(), mock_data_source_resolver)


@pytest.fixture
def expected_mention(markdown_grammar: MarkdownGrammar):
    def _format(name: str) -> str:
        return (
            f"{markdown_grammar.datasource_mention_prefix}"
            f"{name}"
            f"{markdown_grammar.mention_suffix}"
        )

    return _format


class TestDataSourceMentionHandlerBasics:
    @pytest.mark.asyncio
    async def test_simple_data_source_mention(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = "Sales Data"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Sales Data")
        mock_data_source_resolver.resolve_id_to_name.assert_called_once_with("ds-123")

    @pytest.mark.asyncio
    async def test_data_source_mention_none(
        self, handler: DataSourceMentionHandler
    ) -> None:
        mention = DataSourceMention(data_source=None)
        result = await handler.handle(mention)
        assert result == ""

    @pytest.mark.asyncio
    async def test_data_source_mention_fallback_to_id(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = None
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-456"))

        result = await handler.handle(mention)

        assert result == expected_mention("ds-456")
        mock_data_source_resolver.resolve_id_to_name.assert_called_once_with("ds-456")


class TestDataSourceMentionHandlerWithSpecialCharacters:
    @pytest.mark.asyncio
    async def test_data_source_name_with_spaces(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = (
            "Customer Analytics Data"
        )
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Customer Analytics Data")

    @pytest.mark.asyncio
    async def test_data_source_name_with_unicode(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = "データ源 📈"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("データ源 📈")

    @pytest.mark.asyncio
    async def test_data_source_name_with_special_markdown_chars(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = (
            "**Production** Data"
        )
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("**Production** Data")

    @pytest.mark.asyncio
    async def test_data_source_name_with_version(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = "API v2.1.0"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("API v2.1.0")


class TestDataSourceMentionHandlerEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_data_source_name(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = ""
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("ds-123")

    @pytest.mark.asyncio
    async def test_data_source_name_with_newlines(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = "Line1\nLine2"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Line1\nLine2")

    @pytest.mark.asyncio
    async def test_very_long_data_source_name(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        long_name = "DataSource" * 100
        mock_data_source_resolver.resolve_id_to_name.return_value = long_name
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        assert result == expected_mention(long_name)

    @pytest.mark.asyncio
    async def test_data_source_id_with_uuid_format(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = None
        uuid_id = "550e8400-e29b-41d4-a716-446655440000"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id=uuid_id))

        result = await handler.handle(mention)

        assert result == expected_mention(uuid_id)


class TestDataSourceMentionHandlerGrammarConsistency:
    @pytest.mark.asyncio
    async def test_uses_grammar_prefix_and_suffix(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        markdown_grammar: MarkdownGrammar,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = "Test DataSource"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-123"))

        result = await handler.handle(mention)

        expected = (
            f"{markdown_grammar.datasource_mention_prefix}"
            f"Test DataSource"
            f"{markdown_grammar.mention_suffix}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_grammar_prefix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.datasource_mention_prefix == "@datasource["

    @pytest.mark.asyncio
    async def test_grammar_suffix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.mention_suffix == "]"


class TestDataSourceMentionHandlerRealWorldExamples:
    @pytest.mark.asyncio
    async def test_analytics_data_source(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = (
            "Google Analytics 2024"
        )
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-ga"))

        result = await handler.handle(mention)

        assert result == expected_mention("Google Analytics 2024")

    @pytest.mark.asyncio
    async def test_database_connection(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = (
            "PostgreSQL - Production"
        )
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-pg"))

        result = await handler.handle(mention)

        assert result == expected_mention("PostgreSQL - Production")

    @pytest.mark.asyncio
    async def test_api_endpoint(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = "REST API /users"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-api"))

        result = await handler.handle(mention)

        assert result == expected_mention("REST API /users")

    @pytest.mark.asyncio
    async def test_csv_import(
        self,
        handler: DataSourceMentionHandler,
        mock_data_source_resolver,
        expected_mention,
    ) -> None:
        mock_data_source_resolver.resolve_id_to_name.return_value = "sales_data.csv"
        mention = DataSourceMention(data_source=MentionDataSourceRef(id="ds-csv"))

        result = await handler.handle(mention)

        assert result == expected_mention("sales_data.csv")
