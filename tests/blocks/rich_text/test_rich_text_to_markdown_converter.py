from unittest.mock import AsyncMock

import pytest

from notionary.blocks.rich_text.name_id_resolver.database_name_id_resolver import DatabaseNameIdResolver
from notionary.blocks.rich_text.name_id_resolver.page_name_id_resolver import PageNameIdResolver
from notionary.blocks.rich_text.name_id_resolver.person_name_id_resolver import PersonNameIdResolver
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.rich_text.rich_text_models import (
    EquationObject,
    LinkObject,
    MentionDate,
    MentionObject,
    MentionPageRef,
    MentionType,
    MentionUserRef,
    RichText,
    RichTextType,
    TextAnnotations,
    TextContent,
)


@pytest.fixture
def mock_page_resolver() -> AsyncMock:
    resolver: PageNameIdResolver = AsyncMock(spec=PageNameIdResolver)
    resolver.resolve_id_to_name.return_value = "Test Page"
    return resolver


@pytest.fixture
def mock_database_resolver() -> AsyncMock:
    resolver: DatabaseNameIdResolver = AsyncMock(spec=DatabaseNameIdResolver)
    resolver.resolve_id_to_name.return_value = "Tasks DB"
    return resolver


@pytest.fixture
def mock_user_resolver() -> AsyncMock:
    resolver: PersonNameIdResolver = AsyncMock(spec=PersonNameIdResolver)
    resolver.resolve_id_to_name.return_value = "John Doe"
    return resolver


@pytest.fixture
def converter(
    mock_page_resolver: AsyncMock, mock_database_resolver: AsyncMock, mock_user_resolver: AsyncMock
) -> RichTextToMarkdownConverter:
    return RichTextToMarkdownConverter(
        page_resolver=mock_page_resolver, database_resolver=mock_database_resolver, person_resolver=mock_user_resolver
    )


class TestRichTextToMarkdownConverter:
    @pytest.mark.asyncio
    async def test_empty_list(self, converter: RichTextToMarkdownConverter) -> None:
        result = await converter.to_markdown([])
        assert result == ""

    @pytest.mark.asyncio
    async def test_plain_text(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Hello world",
                text=TextContent(content="Hello world"),
                annotations=TextAnnotations(),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_bold_text(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Bold",
                text=TextContent(content="Bold"),
                annotations=TextAnnotations(bold=True),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "**Bold**"

    @pytest.mark.asyncio
    async def test_italic_text(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Italic",
                text=TextContent(content="Italic"),
                annotations=TextAnnotations(italic=True),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "*Italic*"

    @pytest.mark.asyncio
    async def test_code_text(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="code",
                text=TextContent(content="code"),
                annotations=TextAnnotations(code=True),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "`code`"

    @pytest.mark.asyncio
    async def test_link(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Google",
                text=TextContent(content="Google", link=LinkObject(url="https://google.com")),
                annotations=TextAnnotations(),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "[Google](https://google.com)"

    @pytest.mark.asyncio
    async def test_equation(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(type=RichTextType.EQUATION, plain_text="E=mc^2", equation=EquationObject(expression="E=mc^2"))
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "$E=mc^2$"

    @pytest.mark.asyncio
    async def test_page_mention(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="Test Page",
                mention=MentionObject(type=MentionType.PAGE, page=MentionPageRef(id="page-123")),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "@page[Test Page]"

    @pytest.mark.asyncio
    async def test_user_mention(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="John Doe",
                mention=MentionObject(type=MentionType.USER, user=MentionUserRef(id="user-123")),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "@user[John Doe]"

    @pytest.mark.asyncio
    async def test_date_mention(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="2024-01-15",
                mention=MentionObject(type=MentionType.DATE, date=MentionDate(start="2024-01-15", end="2024-01-20")),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "@date[2024-01-15–2024-01-20]"

    @pytest.mark.asyncio
    async def test_mixed_content(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.TEXT,
                plain_text="Hello ",
                text=TextContent(content="Hello "),
                annotations=TextAnnotations(),
            ),
            RichText(
                type=RichTextType.TEXT,
                plain_text="world",
                text=TextContent(content="world"),
                annotations=TextAnnotations(bold=True),
            ),
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "Hello **world**"
