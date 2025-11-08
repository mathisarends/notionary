import pytest

from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.handlers.text import (
    TextHandler,
)
from notionary.rich_text.schemas import (
    RichText,
    RichTextType,
    TextAnnotations,
    TextContent,
)


@pytest.fixture
def handler() -> TextHandler:
    return TextHandler(MarkdownGrammar())


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def expected_format(markdown_grammar: MarkdownGrammar):
    def _format(
        text: str,
        bold: bool = False,
        italic: bool = False,
        code: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
    ) -> str:
        result = text

        if code:
            result = f"{markdown_grammar.code_wrapper}{result}{markdown_grammar.code_wrapper}"

        if strikethrough:
            result = f"{markdown_grammar.strikethrough_wrapper}{result}{markdown_grammar.strikethrough_wrapper}"

        if italic:
            result = f"{markdown_grammar.italic_wrapper}{result}{markdown_grammar.italic_wrapper}"

        if underline:
            result = f"{markdown_grammar.underline_wrapper}{result}{markdown_grammar.underline_wrapper}"

        if bold:
            result = f"{markdown_grammar.bold_wrapper}{result}{markdown_grammar.bold_wrapper}"

        return result

    return _format


class TestTextHandlerBasics:
    @pytest.mark.asyncio
    async def test_plain_text_without_formatting(self, handler: TextHandler) -> None:
        rich_text = RichText.from_plain_text("Hello World")
        result = await handler.handle(rich_text)
        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_empty_text(self, handler: TextHandler) -> None:
        rich_text = RichText.from_plain_text("")
        result = await handler.handle(rich_text)
        assert result == ""

    @pytest.mark.asyncio
    async def test_text_with_none_annotations(self, handler: TextHandler) -> None:
        rich_text = RichText(
            type=RichTextType.TEXT,
            text=TextContent(content="Test"),
            plain_text="Test",
            annotations=None,
        )
        result = await handler.handle(rich_text)
        assert result == "Test"


class TestTextHandlerBoldFormatting:
    @pytest.mark.asyncio
    async def test_bold_text(self, handler: TextHandler, expected_format) -> None:
        rich_text = RichText.from_plain_text("Bold text", bold=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("Bold text", bold=True)

    @pytest.mark.asyncio
    async def test_bold_with_special_characters(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text("Bold & *special*", bold=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("Bold & *special*", bold=True)


class TestTextHandlerItalicFormatting:
    @pytest.mark.asyncio
    async def test_italic_text(self, handler: TextHandler, expected_format) -> None:
        rich_text = RichText.from_plain_text("Italic text", italic=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("Italic text", italic=True)

    @pytest.mark.asyncio
    async def test_italic_with_spaces(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text(" italic ", italic=True)
        result = await handler.handle(rich_text)
        assert result == expected_format(" italic ", italic=True)


class TestTextHandlerCodeFormatting:
    @pytest.mark.asyncio
    async def test_code_text(self, handler: TextHandler, expected_format) -> None:
        rich_text = RichText.from_plain_text("code_snippet", code=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("code_snippet", code=True)

    @pytest.mark.asyncio
    async def test_code_with_backticks(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text("x = `value`", code=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("x = `value`", code=True)


class TestTextHandlerUnderlineFormatting:
    @pytest.mark.asyncio
    async def test_underline_text(self, handler: TextHandler, expected_format) -> None:
        rich_text = RichText.from_plain_text("Underlined", underline=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("Underlined", underline=True)


class TestTextHandlerStrikethroughFormatting:
    @pytest.mark.asyncio
    async def test_strikethrough_text(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text("Crossed out", strikethrough=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("Crossed out", strikethrough=True)


class TestTextHandlerCombinedFormatting:
    @pytest.mark.asyncio
    async def test_bold_and_italic(self, handler: TextHandler, expected_format) -> None:
        rich_text = RichText.from_plain_text("Bold Italic", bold=True, italic=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("Bold Italic", bold=True, italic=True)

    @pytest.mark.asyncio
    async def test_bold_italic_underline(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text(
            "All three", bold=True, italic=True, underline=True
        )
        result = await handler.handle(rich_text)
        assert result == expected_format(
            "All three", bold=True, italic=True, underline=True
        )

    @pytest.mark.asyncio
    async def test_code_with_bold_ignored(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text("code", code=True, bold=True)
        result = await handler.handle(rich_text)
        assert result == expected_format("code", code=True, bold=True)

    @pytest.mark.asyncio
    async def test_strikethrough_with_italic(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text(
            "crossed italic", strikethrough=True, italic=True
        )
        result = await handler.handle(rich_text)
        assert result == expected_format(
            "crossed italic", strikethrough=True, italic=True
        )

    @pytest.mark.asyncio
    async def test_all_formatting_combined(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText.from_plain_text(
            "everything",
            bold=True,
            italic=True,
            underline=True,
            strikethrough=True,
            code=True,
        )
        result = await handler.handle(rich_text)
        assert result == expected_format(
            "everything",
            bold=True,
            italic=True,
            underline=True,
            strikethrough=True,
            code=True,
        )


class TestTextHandlerLinkFormatting:
    @pytest.mark.asyncio
    async def test_simple_link(
        self, handler: TextHandler, markdown_grammar: MarkdownGrammar
    ) -> None:
        rich_text = RichText.for_link("Google", "https://google.com")
        result = await handler.handle(rich_text)
        expected = (
            f"{markdown_grammar.link_prefix}Google{markdown_grammar.link_middle}"
            f"https://google.com{markdown_grammar.link_suffix}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_link_with_bold(
        self, handler: TextHandler, markdown_grammar: MarkdownGrammar, expected_format
    ) -> None:
        rich_text = RichText.for_link("Bold Link", "https://example.com", bold=True)
        result = await handler.handle(rich_text)
        link_part = (
            f"{markdown_grammar.link_prefix}Bold Link{markdown_grammar.link_middle}"
            f"https://example.com{markdown_grammar.link_suffix}"
        )
        expected = expected_format(link_part, bold=True)
        assert result == expected

    @pytest.mark.asyncio
    async def test_link_with_multiple_formatting(
        self, handler: TextHandler, markdown_grammar: MarkdownGrammar, expected_format
    ) -> None:
        rich_text = RichText.for_link(
            "Formatted Link", "https://example.com", bold=True, italic=True
        )
        result = await handler.handle(rich_text)
        link_part = (
            f"{markdown_grammar.link_prefix}Formatted Link{markdown_grammar.link_middle}"
            f"https://example.com{markdown_grammar.link_suffix}"
        )
        expected = expected_format(link_part, bold=True, italic=True)
        assert result == expected

    @pytest.mark.asyncio
    async def test_link_with_empty_text(
        self, handler: TextHandler, markdown_grammar: MarkdownGrammar
    ) -> None:
        rich_text = RichText.for_link("", "https://example.com")
        result = await handler.handle(rich_text)
        expected = (
            f"{markdown_grammar.link_prefix}{markdown_grammar.link_middle}"
            f"https://example.com{markdown_grammar.link_suffix}"
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_link_with_special_chars_in_url(
        self, handler: TextHandler, markdown_grammar: MarkdownGrammar
    ) -> None:
        rich_text = RichText.for_link(
            "Search", "https://example.com/search?q=test&lang=en"
        )
        result = await handler.handle(rich_text)
        expected = (
            f"{markdown_grammar.link_prefix}Search{markdown_grammar.link_middle}"
            f"https://example.com/search?q=test&lang=en{markdown_grammar.link_suffix}"
        )
        assert result == expected


class TestTextHandlerEdgeCases:
    @pytest.mark.asyncio
    async def test_text_with_whitespace_only(self, handler: TextHandler) -> None:
        rich_text = RichText.from_plain_text("   ")
        result = await handler.handle(rich_text)
        assert result == "   "

    @pytest.mark.asyncio
    async def test_text_with_newlines(self, handler: TextHandler) -> None:
        rich_text = RichText.from_plain_text("Line 1\nLine 2")
        result = await handler.handle(rich_text)
        assert result == "Line 1\nLine 2"

    @pytest.mark.asyncio
    async def test_text_with_unicode(self, handler: TextHandler) -> None:
        rich_text = RichText.from_plain_text("Hello 世界 🌍", bold=True)
        result = await handler.handle(rich_text)
        assert result == "**Hello 世界 🌍**"

    @pytest.mark.asyncio
    async def test_rich_text_with_empty_plain_text_but_with_text_content(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText(
            type=RichTextType.TEXT,
            text=TextContent(content="Fallback content"),
            plain_text="",
            annotations=TextAnnotations(bold=True),
        )
        result = await handler.handle(rich_text)
        assert result == expected_format("Fallback content", bold=True)

    @pytest.mark.asyncio
    async def test_rich_text_with_empty_plain_text_and_no_text_content(
        self, handler: TextHandler
    ) -> None:
        rich_text = RichText(
            type=RichTextType.TEXT,
            text=TextContent(content=""),
            plain_text="",
            annotations=TextAnnotations(),
        )
        result = await handler.handle(rich_text)
        assert result == ""


class TestTextHandlerColorHandling:
    @pytest.mark.asyncio
    async def test_text_with_color_annotation_ignored(
        self, handler: TextHandler, expected_format
    ) -> None:
        rich_text = RichText(
            type=RichTextType.TEXT,
            text=TextContent(content="Colored text"),
            plain_text="Colored text",
            annotations=TextAnnotations(bold=True, color="red"),
        )
        result = await handler.handle(rich_text)
        assert result == expected_format("Colored text", bold=True)
        assert "==" not in result
