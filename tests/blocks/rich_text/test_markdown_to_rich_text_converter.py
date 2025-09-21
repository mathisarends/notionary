from unittest.mock import AsyncMock

import pytest

from notionary.blocks.rich_text.database_name_id_resolver import DatabaseNameIdResolver
from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.page_name_id_resolver import PageNameIdResolver
from notionary.blocks.rich_text.rich_text_models import (
    MentionType,
    RichTextType,
)
from notionary.blocks.rich_text.user_name_id_resolver import UserNameIdResolver


@pytest.fixture
def mock_page_resolver() -> AsyncMock:
    resolver: PageNameIdResolver = AsyncMock(spec=PageNameIdResolver)
    resolver.resolve_page_id.return_value = "page-123"
    return resolver


@pytest.fixture
def mock_database_resolver() -> AsyncMock:
    resolver: DatabaseNameIdResolver = AsyncMock(spec=DatabaseNameIdResolver)
    resolver.resolve_database_id.return_value = "db-456"
    return resolver


@pytest.fixture
def mock_user_resolver() -> AsyncMock:
    resolver: UserNameIdResolver = AsyncMock(spec=UserNameIdResolver)
    resolver.resolve_user_id.return_value = "user-789"
    return resolver


@pytest.fixture
def converter(
    mock_page_resolver: AsyncMock, mock_database_resolver: AsyncMock, mock_user_resolver: AsyncMock
) -> MarkdownRichTextConverter:
    return MarkdownRichTextConverter(
        page_resolver=mock_page_resolver, database_resolver=mock_database_resolver, user_resolver=mock_user_resolver
    )


class TestMarkdownRichTextConverter:
    @pytest.mark.asyncio
    async def test_empty_string(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("")
        assert result == []

    @pytest.mark.asyncio
    async def test_plain_text(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("Hello world")
        assert len(result) == 1
        assert result[0].type == RichTextType.TEXT
        assert result[0].plain_text == "Hello world"
        assert result[0].annotations.bold is False

    @pytest.mark.asyncio
    async def test_bold_text(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("**bold**")
        assert len(result) == 1
        assert result[0].type == RichTextType.TEXT
        assert result[0].plain_text == "bold"
        assert result[0].annotations.bold is True

    @pytest.mark.asyncio
    async def test_italic_text(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("*italic*")
        assert len(result) == 1
        assert result[0].type == RichTextType.TEXT
        assert result[0].plain_text == "italic"
        assert result[0].annotations.italic is True

    @pytest.mark.asyncio
    async def test_code_text(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("`code`")
        assert len(result) == 1
        assert result[0].type == RichTextType.TEXT
        assert result[0].plain_text == "code"
        assert result[0].annotations.code is True

    @pytest.mark.asyncio
    async def test_link(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("[Google](https://google.com)")
        assert len(result) == 1
        assert result[0].type == RichTextType.TEXT
        assert result[0].plain_text == "Google"
        assert result[0].text.link.url == "https://google.com"

    @pytest.mark.asyncio
    async def test_equation(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("$E=mc^2$")
        assert len(result) == 1
        assert result[0].type == RichTextType.EQUATION
        assert result[0].equation.expression == "E=mc^2"

    @pytest.mark.asyncio
    async def test_page_mention(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("@page[Test Page]")
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert result[0].mention.type == MentionType.PAGE
        assert result[0].mention.page.id == "page-123"

    @pytest.mark.asyncio
    async def test_user_mention(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("@user[John Doe]")
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert result[0].mention.type == MentionType.USER
        assert result[0].mention.user.id == "user-789"

    @pytest.mark.asyncio
    async def test_mixed_content(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("Hello **bold** world")
        assert len(result) == 3
        assert result[0].plain_text == "Hello "
        assert result[0].annotations.bold is False
        assert result[1].plain_text == "bold"
        assert result[1].annotations.bold is True
        assert result[2].plain_text == " world"
        assert result[2].annotations.bold is False

    @pytest.mark.asyncio
    async def test_colored_text(self, converter: MarkdownRichTextConverter) -> None:
        result = await converter.to_rich_text("(red:Important)")
        assert len(result) == 1
        assert result[0].plain_text == "Important"
        assert result[0].annotations.color == "red"

    @pytest.mark.asyncio
    async def test_unresolved_mention_fallback(
        self, converter: MarkdownRichTextConverter, mock_page_resolver: AsyncMock
    ) -> None:
        mock_page_resolver.resolve_page_id.return_value = None
        result = await converter.to_rich_text("@page[Unknown Page]")
        assert len(result) == 1
        assert result[0].type == RichTextType.TEXT
        assert result[0].plain_text == "@page[Unknown Page]"
