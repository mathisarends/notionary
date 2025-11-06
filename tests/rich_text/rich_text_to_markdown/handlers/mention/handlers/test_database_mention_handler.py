from unittest.mock import AsyncMock

import pytest

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.handlers.mention.handlers.database import (
    DatabaseMentionHandler,
)
from notionary.rich_text.schemas import DatabaseMention, MentionDatabaseRef


@pytest.fixture
def mock_database_resolver():
    resolver = AsyncMock()
    resolver.resolve_id_to_name = AsyncMock()
    return resolver


@pytest.fixture
def handler(mock_database_resolver) -> DatabaseMentionHandler:
    return DatabaseMentionHandler(MarkdownGrammar(), mock_database_resolver)


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def expected_mention(markdown_grammar: MarkdownGrammar):
    def _format(name: str) -> str:
        return (
            f"{markdown_grammar.database_mention_prefix}"
            f"{name}"
            f"{markdown_grammar.mention_suffix}"
        )

    return _format


class TestDatabaseMentionHandlerBasics:
    @pytest.mark.asyncio
    async def test_simple_database_mention(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "Tasks Database"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Tasks Database")
        mock_database_resolver.resolve_id_to_name.assert_called_once_with("db-123")

    @pytest.mark.asyncio
    async def test_database_mention_none(self, handler: DatabaseMentionHandler) -> None:
        mention = DatabaseMention(database=None)
        result = await handler.handle(mention)
        assert result == ""

    @pytest.mark.asyncio
    async def test_database_mention_fallback_to_id(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = None
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-456"))

        result = await handler.handle(mention)

        assert result == expected_mention("db-456")
        mock_database_resolver.resolve_id_to_name.assert_called_once_with("db-456")


class TestDatabaseMentionHandlerWithSpecialCharacters:
    @pytest.mark.asyncio
    async def test_database_name_with_spaces(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "My Tasks Database"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("My Tasks Database")

    @pytest.mark.asyncio
    async def test_database_name_with_unicode(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "データベース 📊"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("データベース 📊")

    @pytest.mark.asyncio
    async def test_database_name_with_special_markdown_chars(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "**Main** Database"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("**Main** Database")

    @pytest.mark.asyncio
    async def test_database_name_with_brackets(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "[Archive] DB"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("[Archive] DB")


class TestDatabaseMentionHandlerEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_database_name(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = ""
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("db-123")

    @pytest.mark.asyncio
    async def test_database_name_with_newlines(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "DB\nLine2"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("DB\nLine2")

    @pytest.mark.asyncio
    async def test_very_long_database_name(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        long_name = "Database " * 100
        mock_database_resolver.resolve_id_to_name.return_value = long_name
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        assert result == expected_mention(long_name)

    @pytest.mark.asyncio
    async def test_database_id_with_uuid_format(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = None
        uuid_id = "123e4567-e89b-12d3-a456-426614174000"
        mention = DatabaseMention(database=MentionDatabaseRef(id=uuid_id))

        result = await handler.handle(mention)

        assert result == expected_mention(uuid_id)


class TestDatabaseMentionHandlerGrammarConsistency:
    @pytest.mark.asyncio
    async def test_uses_grammar_prefix_and_suffix(
        self,
        handler: DatabaseMentionHandler,
        mock_database_resolver,
        markdown_grammar: MarkdownGrammar,
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "Test DB"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-123"))

        result = await handler.handle(mention)

        expected = (
            f"{markdown_grammar.database_mention_prefix}"
            f"Test DB"
            f"{markdown_grammar.mention_suffix}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_grammar_prefix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.database_mention_prefix == "@database["

    @pytest.mark.asyncio
    async def test_grammar_suffix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.mention_suffix == "]"


class TestDatabaseMentionHandlerRealWorldExamples:
    @pytest.mark.asyncio
    async def test_projects_database_mention(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "Projects 2024"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-proj"))

        result = await handler.handle(mention)

        assert result == expected_mention("Projects 2024")

    @pytest.mark.asyncio
    async def test_contacts_database_mention(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "Contacts & Clients"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-contacts"))

        result = await handler.handle(mention)

        assert result == expected_mention("Contacts & Clients")

    @pytest.mark.asyncio
    async def test_inventory_database_mention(
        self, handler: DatabaseMentionHandler, mock_database_resolver, expected_mention
    ) -> None:
        mock_database_resolver.resolve_id_to_name.return_value = "Inventory (Q1)"
        mention = DatabaseMention(database=MentionDatabaseRef(id="db-inv"))

        result = await handler.handle(mention)

        assert result == expected_mention("Inventory (Q1)")
