import pytest

from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.schemas import (
    DateMention,
    EquationObject,
    LinkObject,
    MentionDate,
    MentionPageRef,
    MentionUserRef,
    PageMention,
    RichText,
    RichTextType,
    TextAnnotations,
    TextContent,
    UserMention,
)


@pytest.fixture
def converter() -> RichTextToMarkdownConverter:
    return RichTextToMarkdownConverter()


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
                text=TextContent(
                    content="Google", link=LinkObject(url="https://google.com")
                ),
                annotations=TextAnnotations(),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "[Google](https://google.com)"

    @pytest.mark.asyncio
    async def test_equation(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.EQUATION,
                plain_text="E=mc^2",
                equation=EquationObject(expression="E=mc^2"),
            )
        ]
        result = await converter.to_markdown(rich_text)
        assert result == "$E=mc^2$"

    @pytest.mark.asyncio
    async def test_page_mention(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="Test Page",
                mention=PageMention(page=MentionPageRef(id="page-123")),
            )
        ]
        result = await converter.to_markdown(rich_text)
        # Falls back to ID since no resolver is mocked
        assert result == "@page[page-123]"

    @pytest.mark.asyncio
    async def test_user_mention(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="John Doe",
                mention=UserMention(user=MentionUserRef(id="user-123")),
            )
        ]
        result = await converter.to_markdown(rich_text)
        # Falls back to ID since no resolver is mocked
        assert result == "@user[user-123]"

    @pytest.mark.asyncio
    async def test_date_mention(self, converter: RichTextToMarkdownConverter) -> None:
        rich_text = [
            RichText(
                type=RichTextType.MENTION,
                plain_text="2024-01-15",
                mention=DateMention(
                    date=MentionDate(start="2024-01-15", end="2024-01-20")
                ),
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
