from unittest.mock import AsyncMock

import pytest

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.rich_text_handlers.handlers.mention.handlers.user import (
    UserMentionHandler,
)
from notionary.rich_text.schemas import MentionUserRef, UserMention


@pytest.fixture
def mock_person_resolver():
    resolver = AsyncMock()
    resolver.resolve_id_to_name = AsyncMock()
    return resolver


@pytest.fixture
def handler(mock_person_resolver) -> UserMentionHandler:
    return UserMentionHandler(MarkdownGrammar(), mock_person_resolver)


@pytest.fixture
def expected_mention(markdown_grammar: MarkdownGrammar):
    def _format(name: str) -> str:
        return (
            f"{markdown_grammar.user_mention_prefix}"
            f"{name}"
            f"{markdown_grammar.mention_suffix}"
        )

    return _format


class TestUserMentionHandlerBasics:
    @pytest.mark.asyncio
    async def test_simple_user_mention(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "John Doe"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("John Doe")
        mock_person_resolver.resolve_id_to_name.assert_called_once_with("user-123")

    @pytest.mark.asyncio
    async def test_user_mention_none(self, handler: UserMentionHandler) -> None:
        mention = UserMention(user=None)
        result = await handler.handle(mention)
        assert result == ""

    @pytest.mark.asyncio
    async def test_user_mention_fallback_to_id(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = None
        mention = UserMention(user=MentionUserRef(id="user-456"))

        result = await handler.handle(mention)

        assert result == expected_mention("user-456")
        mock_person_resolver.resolve_id_to_name.assert_called_once_with("user-456")


class TestUserMentionHandlerWithSpecialCharacters:
    @pytest.mark.asyncio
    async def test_user_name_with_spaces(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "Jane Marie Smith"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Jane Marie Smith")

    @pytest.mark.asyncio
    async def test_user_name_with_unicode(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "François Müller 中文"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("François Müller 中文")

    @pytest.mark.asyncio
    async def test_user_name_with_special_chars(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "O'Brien-Smith"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("O'Brien-Smith")

    @pytest.mark.asyncio
    async def test_user_name_with_emoji(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "Alex 👨‍💻"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Alex 👨‍💻")


class TestUserMentionHandlerEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_user_name(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = ""
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("user-123")

    @pytest.mark.asyncio
    async def test_user_name_with_newlines(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "First\nLast"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("First\nLast")

    @pytest.mark.asyncio
    async def test_very_long_user_name(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        long_name = "VeryLongUserName" * 50
        mock_person_resolver.resolve_id_to_name.return_value = long_name
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention(long_name)

    @pytest.mark.asyncio
    async def test_user_id_with_uuid_format(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = None
        uuid_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        mention = UserMention(user=MentionUserRef(id=uuid_id))

        result = await handler.handle(mention)

        assert result == expected_mention(uuid_id)


class TestUserMentionHandlerGrammarConsistency:
    @pytest.mark.asyncio
    async def test_uses_grammar_prefix_and_suffix(
        self,
        handler: UserMentionHandler,
        mock_person_resolver,
        markdown_grammar: MarkdownGrammar,
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "Test User"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        expected = (
            f"{markdown_grammar.user_mention_prefix}"
            f"Test User"
            f"{markdown_grammar.mention_suffix}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_grammar_prefix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.user_mention_prefix == "@user["

    @pytest.mark.asyncio
    async def test_grammar_suffix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.mention_suffix == "]"


class TestUserMentionHandlerRealWorldExamples:
    @pytest.mark.asyncio
    async def test_team_member_mention(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "Sarah Johnson"
        mention = UserMention(user=MentionUserRef(id="user-sarah"))

        result = await handler.handle(mention)

        assert result == expected_mention("Sarah Johnson")

    @pytest.mark.asyncio
    async def test_single_name_user(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "Madonna"
        mention = UserMention(user=MentionUserRef(id="user-madonna"))

        result = await handler.handle(mention)

        assert result == expected_mention("Madonna")

    @pytest.mark.asyncio
    async def test_email_as_user_identifier(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "user@example.com"
        mention = UserMention(user=MentionUserRef(id="user-email-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("user@example.com")

    @pytest.mark.asyncio
    async def test_username_with_at_symbol(
        self, handler: UserMentionHandler, mock_person_resolver, expected_mention
    ) -> None:
        mock_person_resolver.resolve_id_to_name.return_value = "@username"
        mention = UserMention(user=MentionUserRef(id="user-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("@username")
