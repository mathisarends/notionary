from collections.abc import Callable
from unittest.mock import AsyncMock

import pytest

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.mention.handlers.page import (
    PageMentionHandler,
)
from notionary.rich_text.schemas import (
    MentionPageRef,
    PageMention,
)


@pytest.fixture
def mock_page_resolver() -> AsyncMock:
    resolver = AsyncMock()
    resolver.resolve_id_to_name = AsyncMock()
    return resolver


@pytest.fixture
def handler(mock_page_resolver: AsyncMock) -> PageMentionHandler:
    return PageMentionHandler(MarkdownGrammar(), mock_page_resolver)


@pytest.fixture
def expected_mention(markdown_grammar: MarkdownGrammar) -> Callable[[str], str]:
    def _format(name: str) -> str:
        return (
            f"{markdown_grammar.page_mention_prefix}"
            f"{name}"
            f"{markdown_grammar.mention_suffix}"
        )

    return _format


class TestPageMentionHandlerBasics:
    @pytest.mark.asyncio
    async def test_simple_page_mention(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "Project Plan"
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Project Plan")
        mock_page_resolver.resolve_id_to_name.assert_called_once_with("page-123")

    @pytest.mark.asyncio
    async def test_page_mention_none(self, handler: PageMentionHandler) -> None:
        mention = PageMention(page=None)
        result = await handler.handle(mention)
        assert result == ""

    @pytest.mark.asyncio
    async def test_page_mention_fallback_to_id(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = None
        mention = PageMention(page=MentionPageRef(id="page-456"))

        result = await handler.handle(mention)

        assert result == expected_mention("page-456")
        mock_page_resolver.resolve_id_to_name.assert_called_once_with("page-456")


class TestPageMentionHandlerWithSpecialCharacters:
    @pytest.mark.asyncio
    async def test_page_name_with_spaces(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "My Project Plan"
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("My Project Plan")

    @pytest.mark.asyncio
    async def test_page_name_with_unicode(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "Projekt 世界 🌍"
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Projekt 世界 🌍")

    @pytest.mark.asyncio
    async def test_page_name_with_special_markdown_chars(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "**Bold** and *Italic*"
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("**Bold** and *Italic*")

    @pytest.mark.asyncio
    async def test_page_name_with_brackets(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "[Important] Notes"
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("[Important] Notes")


class TestPageMentionHandlerEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_page_name(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = ""
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("page-123")

    @pytest.mark.asyncio
    async def test_page_name_with_newlines(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "Line1\nLine2"
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention("Line1\nLine2")

    @pytest.mark.asyncio
    async def test_very_long_page_name(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        long_name = "A" * 1000
        mock_page_resolver.resolve_id_to_name.return_value = long_name
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        assert result == expected_mention(long_name)

    @pytest.mark.asyncio
    async def test_page_id_with_special_format(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = None
        special_id = "550e8400-e29b-41d4-a716-446655440000"
        mention = PageMention(page=MentionPageRef(id=special_id))

        result = await handler.handle(mention)

        assert result == expected_mention(special_id)


class TestPageMentionHandlerGrammarConsistency:
    @pytest.mark.asyncio
    async def test_uses_grammar_prefix_and_suffix(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        markdown_grammar: MarkdownGrammar,
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "Test Page"
        mention = PageMention(page=MentionPageRef(id="page-123"))

        result = await handler.handle(mention)

        expected = (
            f"{markdown_grammar.page_mention_prefix}"
            f"Test Page"
            f"{markdown_grammar.mention_suffix}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_grammar_prefix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.page_mention_prefix == "@page["

    @pytest.mark.asyncio
    async def test_grammar_suffix_is_correct(
        self, markdown_grammar: MarkdownGrammar
    ) -> None:
        assert markdown_grammar.mention_suffix == "]"


class TestPageMentionHandlerRealWorldExamples:
    @pytest.mark.asyncio
    async def test_meeting_notes_mention(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "Meeting Notes - Q4 2024"
        mention = PageMention(page=MentionPageRef(id="page-abc"))

        result = await handler.handle(mention)

        assert result == expected_mention("Meeting Notes - Q4 2024")

    @pytest.mark.asyncio
    async def test_documentation_page_mention(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "API Documentation v2.0"
        mention = PageMention(page=MentionPageRef(id="page-def"))

        result = await handler.handle(mention)

        assert result == expected_mention("API Documentation v2.0")

    @pytest.mark.asyncio
    async def test_task_page_mention(
        self,
        handler: PageMentionHandler,
        mock_page_resolver: AsyncMock,
        expected_mention: Callable[[str], str],
    ) -> None:
        mock_page_resolver.resolve_id_to_name.return_value = "TODO: Refactor Rich Text"
        mention = PageMention(page=MentionPageRef(id="page-ghi"))

        result = await handler.handle(mention)

        assert result == expected_mention("TODO: Refactor Rich Text")
