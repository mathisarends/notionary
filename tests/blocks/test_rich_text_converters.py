import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.rich_text.rich_text_models import RichTextType


class TestMarkdownRichTextConverter:
    """Test MarkdownRichTextConverter for converting markdown to RichTextObjects."""

    @pytest.mark.parametrize(
        "markdown,expected_text,expected_bold",
        [
            ("**bold text**", "bold text", True),
            ("**multiple words**", "multiple words", True),
            ("**Umlaute äöü**", "Umlaute äöü", True),
        ],
    )
    @pytest.mark.asyncio
    async def test_bold_formatting(self, markdown, expected_text, expected_bold):
        """Test bold text parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text(markdown)
        assert len(result) == 1
        assert result[0].plain_text == expected_text
        assert result[0].annotations.bold == expected_bold

    @pytest.mark.parametrize(
        "markdown,expected_text",
        [
            ("*italic text*", "italic text"),
            ("_italic underscore_", "italic underscore"),
            ("*🙂 emoji*", "🙂 emoji"),
        ],
    )
    @pytest.mark.asyncio
    async def test_italic_formatting(self, markdown, expected_text):
        """Test italic text parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text(markdown)
        assert len(result) == 1
        assert result[0].plain_text == expected_text
        assert result[0].annotations.italic is True

    @pytest.mark.asyncio
    async def test_underline_formatting(self):
        """Test underline text parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("__underlined__")
        assert len(result) == 1
        assert result[0].plain_text == "underlined"
        assert result[0].annotations.underline is True

    @pytest.mark.asyncio
    async def test_strikethrough_formatting(self):
        """Test strikethrough text parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("~~crossed out~~")
        assert len(result) == 1
        assert result[0].plain_text == "crossed out"
        assert result[0].annotations.strikethrough is True

    @pytest.mark.asyncio
    async def test_code_formatting(self):
        """Test inline code parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("`code snippet`")
        assert len(result) == 1
        assert result[0].plain_text == "code snippet"
        assert result[0].annotations.code is True

    @pytest.mark.asyncio
    async def test_simple_link(self):
        """Test basic link parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("[text](https://example.com)")
        assert len(result) == 1
        assert result[0].plain_text == "text"
        assert result[0].text.link.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_inline_equation(self):
        """Test inline equation parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("$E = mc^2$")
        assert len(result) == 1
        assert result[0].type == RichTextType.EQUATION
        assert result[0].equation.expression == "E = mc^2"

    @pytest.mark.asyncio
    async def test_valid_color(self):
        """Test valid color parsing."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("(red:important)")
        assert len(result) == 1
        assert result[0].plain_text == "important"
        assert result[0].annotations.color == "red"

    @pytest.mark.asyncio
    async def test_invalid_color_fallback(self):
        """Test invalid color falls back to plain text."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("(invalid:text)")
        assert len(result) == 1
        assert result[0].plain_text == "(invalid:text)"

    @pytest.mark.asyncio
    async def test_empty_input(self):
        """Test empty input handling."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("")
        assert result == []

    @pytest.mark.asyncio
    async def test_plain_text_only(self):
        """Test plain text without formatting."""
        converter = MarkdownRichTextConverter()
        result = await converter.to_rich_text("Just plain text")
        assert len(result) == 1
        assert result[0].plain_text == "Just plain text"
        assert not result[0].annotations.bold
        assert not result[0].annotations.italic


class TestRichTextToMarkdownConverter:
    """Test RichTextToMarkdownConverter for converting RichTextObjects to markdown."""

    @pytest.mark.asyncio
    async def test_bold_to_markdown(self):
        """Test converting bold rich text to markdown."""
        converter = RichTextToMarkdownConverter()

        # Create bold rich text manually
        from notionary.blocks.rich_text.rich_text_models import RichText

        rich_text = [RichText.from_plain_text("bold text", bold=True)]

        result = await converter.to_markdown(rich_text)
        assert result == "**bold text**"

    @pytest.mark.asyncio
    async def test_italic_to_markdown(self):
        """Test converting italic rich text to markdown."""
        converter = RichTextToMarkdownConverter()

        from notionary.blocks.rich_text.rich_text_models import RichText

        rich_text = [RichText.from_plain_text("italic text", italic=True)]

        result = await converter.to_markdown(rich_text)
        assert result == "*italic text*"

    @pytest.mark.asyncio
    async def test_link_to_markdown(self):
        """Test converting link rich text to markdown."""
        converter = RichTextToMarkdownConverter()

        from notionary.blocks.rich_text.rich_text_models import RichText

        rich_text = [RichText.for_link("text", "https://example.com")]

        result = await converter.to_markdown(rich_text)
        assert result == "[text](https://example.com)"

    @pytest.mark.asyncio
    async def test_equation_to_markdown(self):
        """Test converting equation rich text to markdown."""
        converter = RichTextToMarkdownConverter()

        from notionary.blocks.rich_text.rich_text_models import RichText

        rich_text = [RichText.equation_inline("E = mc^2")]

        result = await converter.to_markdown(rich_text)
        assert result == "$E = mc^2$"

    @pytest.mark.asyncio
    async def test_colored_text_to_markdown(self):
        """Test converting colored rich text to markdown."""
        converter = RichTextToMarkdownConverter()

        from notionary.blocks.rich_text.rich_text_models import RichText

        rich_text = [RichText.from_plain_text("important", color="red")]

        result = await converter.to_markdown(rich_text)
        assert result == "(red:important)"

    @pytest.mark.asyncio
    async def test_empty_rich_text(self):
        """Test empty rich text handling."""
        converter = RichTextToMarkdownConverter()
        result = await converter.to_markdown([])
        assert result == ""

    @pytest.mark.asyncio
    async def test_plain_text_to_markdown(self):
        """Test converting plain rich text to markdown."""
        converter = RichTextToMarkdownConverter()

        from notionary.blocks.rich_text.rich_text_models import RichText

        rich_text = [RichText.from_plain_text("Just plain text")]

        result = await converter.to_markdown(rich_text)
        assert result == "Just plain text"


class TestRoundtripConversion:
    """Test roundtrip conversion: markdown -> rich text -> markdown."""

    @pytest.mark.parametrize(
        "markdown",
        [
            "**bold text**",
            "*italic text*",
            "__underlined text__",
            "~~strikethrough~~",
            "`code snippet`",
            "[link](https://example.com)",
            "$E = mc^2$",
            "(red:colored text)",
            "(blue_background:highlighted)",
        ],
    )
    @pytest.mark.asyncio
    async def test_simple_roundtrip(self, markdown):
        """Test that simple markdown formats survive roundtrip conversion."""
        markdown_converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        # Convert markdown to rich text and back
        rich_objects = await markdown_converter.to_rich_text(markdown)
        back_to_markdown = await rich_text_converter.to_markdown(rich_objects)

        assert back_to_markdown == markdown

    @pytest.mark.asyncio
    async def test_complex_roundtrip(self):
        """Test complex mixed formatting survives roundtrip."""
        markdown = "This is **bold** and *italic* and `code`"

        markdown_converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        rich_objects = await markdown_converter.to_rich_text(markdown)
        back_to_markdown = await rich_text_converter.to_markdown(rich_objects)

        # Should contain all formatting elements
        assert "**bold**" in back_to_markdown
        assert "*italic*" in back_to_markdown
        assert "`code`" in back_to_markdown

    @pytest.mark.asyncio
    async def test_mixed_content_roundtrip(self):
        """Test mixed content with text and formatting survives roundtrip."""
        markdown = "Start **bold** middle *italic* end"

        markdown_converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        rich_objects = await markdown_converter.to_rich_text(markdown)
        back_to_markdown = await rich_text_converter.to_markdown(rich_objects)

        assert "Start " in back_to_markdown
        assert "**bold**" in back_to_markdown
        assert " middle " in back_to_markdown
        assert "*italic*" in back_to_markdown
        assert " end" in back_to_markdown


class TestConverterEdgeCases:
    """Test edge cases and error conditions for both converters."""

    @pytest.mark.asyncio
    async def test_nested_formatting_priority(self):
        """Test that nested formatting is handled properly."""
        markdown_converter = MarkdownRichTextConverter()
        result = await markdown_converter.to_rich_text("**bold *and* text**")

        # Should handle nested formatting gracefully
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_unicode_and_special_chars(self):
        """Test handling of Unicode and special characters."""
        markdown_converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        markdown = "**Unicode: äöü 🙂 §**"

        rich_objects = await markdown_converter.to_rich_text(markdown)
        back_to_markdown = await rich_text_converter.to_markdown(rich_objects)

        assert "äöü" in back_to_markdown
        assert "🙂" in back_to_markdown
        assert "§" in back_to_markdown

    @pytest.mark.asyncio
    async def test_whitespace_handling(self):
        """Test proper whitespace handling."""
        markdown_converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        markdown = "  **bold**  "

        rich_objects = await markdown_converter.to_rich_text(markdown)
        back_to_markdown = await rich_text_converter.to_markdown(rich_objects)

        # Should preserve meaningful whitespace
        assert "**bold**" in back_to_markdown
