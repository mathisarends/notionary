# TODO: Test this file here which would be nice:
from unittest.mock import Mock

import pytest

from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.rich_text.rich_text_models import RichTextObject, RichTextType
from notionary.blocks.types import BlockColor


class TestTextInlineFormatterBasics:
    """Test basic formatting patterns."""

    @pytest.mark.parametrize(
        "markdown,expected_text,expected_bold",
        [
            ("**bold text**", "bold text", True),
            ("**multiple words**", "multiple words", True),
            ("**Umlaute äöü**", "Umlaute äöü", True),
        ],
    )
    def test_bold_formatting(self, markdown, expected_text, expected_bold):
        """Test bold text parsing."""
        result = TextInlineFormatter.parse_inline_formatting(markdown)
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
    def test_italic_formatting(self, markdown, expected_text):
        """Test italic text parsing."""
        result = TextInlineFormatter.parse_inline_formatting(markdown)
        assert len(result) == 1
        assert result[0].plain_text == expected_text
        assert result[0].annotations.italic is True

    def test_underline_formatting(self):
        """Test underline text parsing."""
        result = TextInlineFormatter.parse_inline_formatting("__underlined__")
        assert len(result) == 1
        assert result[0].plain_text == "underlined"
        assert result[0].annotations.underline is True

    def test_strikethrough_formatting(self):
        """Test strikethrough text parsing."""
        result = TextInlineFormatter.parse_inline_formatting("~~crossed out~~")
        assert len(result) == 1
        assert result[0].plain_text == "crossed out"
        assert result[0].annotations.strikethrough is True

    def test_code_formatting(self):
        """Test inline code parsing."""
        result = TextInlineFormatter.parse_inline_formatting("`code snippet`")
        assert len(result) == 1
        assert result[0].plain_text == "code snippet"
        assert result[0].annotations.code is True


class TestTextInlineFormatterLinks:
    """Test link parsing."""

    def test_simple_link(self):
        """Test basic link parsing."""
        result = TextInlineFormatter.parse_inline_formatting("[text](https://example.com)")
        assert len(result) == 1
        assert result[0].plain_text == "text"
        assert result[0].text.link.url == "https://example.com"

    @pytest.mark.parametrize(
        "markdown,expected_text,expected_url",
        [
            ("[GitHub](https://github.com)", "GitHub", "https://github.com"),
            ("[Notion](https://notion.so)", "Notion", "https://notion.so"),
            ("[Local](http://localhost:3000)", "Local", "http://localhost:3000"),
        ],
    )
    def test_link_variations(self, markdown, expected_text, expected_url):
        """Test various link formats."""
        result = TextInlineFormatter.parse_inline_formatting(markdown)
        assert len(result) == 1
        assert result[0].plain_text == expected_text
        assert result[0].text.link.url == expected_url


class TestTextInlineFormatterEquations:
    """Test inline equation parsing."""

    @pytest.mark.parametrize(
        "markdown,expected_expression",
        [
            ("$E = mc^2$", "E = mc^2"),
            ("$\\frac{a}{b}$", "\\frac{a}{b}"),
            ("$\\sum_{i=1}^n i$", "\\sum_{i=1}^n i"),
        ],
    )
    def test_inline_equations(self, markdown, expected_expression):
        """Test inline equation parsing."""
        result = TextInlineFormatter.parse_inline_formatting(markdown)
        assert len(result) == 1
        assert result[0].type == RichTextType.EQUATION
        assert result[0].equation.expression == expected_expression


class TestTextInlineFormatterColors:
    """Test color formatting."""

    @pytest.mark.parametrize(
        "markdown,expected_text,expected_color",
        [
            ("(red:important)", "important", "red"),
            ("(blue:information)", "information", "blue"),
            ("(yellow_background:highlight)", "highlight", "yellow_background"),
            ("(green_background:success)", "success", "green_background"),
        ],
    )
    def test_valid_colors(self, markdown, expected_text, expected_color):
        """Test valid color parsing."""
        result = TextInlineFormatter.parse_inline_formatting(markdown)
        assert len(result) == 1
        assert result[0].plain_text == expected_text
        assert result[0].annotations.color == expected_color

    def test_invalid_color_fallback(self):
        """Test invalid color falls back to plain text."""
        result = TextInlineFormatter.parse_inline_formatting("(invalid:text)")
        assert len(result) == 1
        assert result[0].plain_text == "(invalid:text)"
        assert result[0].annotations.color == "default"


class TestTextInlineFormatterMentions:
    """Test page mention parsing."""

    def test_page_mention(self):
        """Test page mention parsing."""
        page_id = "123e4567-e89b-12d3-a456-426614174000"
        result = TextInlineFormatter.parse_inline_formatting(f"@[{page_id}]")
        assert len(result) == 1
        assert result[0].type == RichTextType.MENTION
        assert result[0].mention.page.id == page_id


class TestTextInlineFormatterComplex:
    """Test complex mixed formatting."""

    def test_mixed_formatting(self):
        """Test multiple formatting types in one text."""
        markdown = "Text with **bold** and *italic* and `code`"
        result = TextInlineFormatter.parse_inline_formatting(markdown)
        
        assert len(result) == 6  # "Text with ", "bold", " and ", "italic", " and ", "code"
        assert result[0].plain_text == "Text with "
        assert result[1].plain_text == "bold"
        assert result[1].annotations.bold is True
        assert result[3].plain_text == "italic"
        assert result[3].annotations.italic is True
        assert result[5].plain_text == "code"
        assert result[5].annotations.code is True

    def test_nested_formatting_priority(self):
        """Test that first pattern wins when patterns overlap."""
        # Bold should take precedence over italic when they overlap
        result = TextInlineFormatter.parse_inline_formatting("**bold *and* text**")
        # Should parse as one bold block, not separate italic inside
        assert len(result) == 1
        assert result[0].plain_text == "bold *and* text"
        assert result[0].annotations.bold is True

    def test_adjacent_formatting(self):
        """Test adjacent formatting blocks."""
        result = TextInlineFormatter.parse_inline_formatting("**bold**__underline__")
        assert len(result) == 2
        assert result[0].annotations.bold is True
        assert result[1].annotations.underline is True

    def test_equation_with_text(self):
        """Test equation mixed with regular text."""
        markdown = "The formula $E = mc^2$ is famous"
        result = TextInlineFormatter.parse_inline_formatting(markdown)
        assert len(result) == 3
        assert result[0].plain_text == "The formula "
        assert result[1].type == RichTextType.EQUATION
        assert result[1].equation.expression == "E = mc^2"
        assert result[2].plain_text == " is famous"


class TestTextInlineFormatterRoundtrip:
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
    def test_simple_roundtrip(self, markdown):
        """Test that simple formatting survives roundtrip conversion."""
        rich_objects = TextInlineFormatter.parse_inline_formatting(markdown)
        back_to_markdown = TextInlineFormatter.extract_text_with_formatting(rich_objects)
        assert back_to_markdown == markdown

    def test_complex_roundtrip(self):
        """Test complex formatting roundtrip."""
        markdown = "Text with **bold** and *italic* and `code` and [link](https://example.com)"
        rich_objects = TextInlineFormatter.parse_inline_formatting(markdown)
        back_to_markdown = TextInlineFormatter.extract_text_with_formatting(rich_objects)
        assert back_to_markdown == markdown

    def test_equation_roundtrip(self):
        """Test equation roundtrip with complex LaTeX."""
        markdown = "$\\sum_{i=1}^n \\frac{i}{2}$"
        rich_objects = TextInlineFormatter.parse_inline_formatting(markdown)
        back_to_markdown = TextInlineFormatter.extract_text_with_formatting(rich_objects)
        assert back_to_markdown == markdown


class TestTextInlineFormatterEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_input(self):
        """Test empty input returns empty list."""
        result = TextInlineFormatter.parse_inline_formatting("")
        assert result == []

    def test_plain_text_only(self):
        """Test plain text without formatting."""
        result = TextInlineFormatter.parse_inline_formatting("just plain text")
        assert len(result) == 1
        assert result[0].plain_text == "just plain text"
        assert not any([
            result[0].annotations.bold,
            result[0].annotations.italic,
            result[0].annotations.underline,
            result[0].annotations.strikethrough,
            result[0].annotations.code,
        ])

    def test_incomplete_patterns(self):
        """Test incomplete formatting patterns are treated as plain text."""
        incomplete_patterns = [
            "**incomplete bold",
            "*incomplete italic",
            "__incomplete underline",
            "~~incomplete strike",
            "`incomplete code",
            "[incomplete link]()",
            "$incomplete equation",
        ]
        for pattern in incomplete_patterns:
            result = TextInlineFormatter.parse_inline_formatting(pattern)
            # Should be treated as plain text if pattern is incomplete
            assert len(result) == 1
            assert result[0].plain_text == pattern

    def test_unicode_and_special_chars(self):
        """Test Unicode and special character handling."""
        test_cases = [
            "**中文粗体**",
            "*🙂 emoji italic*",
            "`special chars !@#$%^&*()`",
            "(red:Umlaute äöü)",
        ]
        for case in test_cases:
            result = TextInlineFormatter.parse_inline_formatting(case)
            # Should parse without errors
            assert len(result) >= 1
            # Roundtrip should work
            back = TextInlineFormatter.extract_text_with_formatting(result)
            assert back == case

    def test_whitespace_handling(self):
        """Test whitespace in formatting patterns."""
        # Leading/trailing spaces in formatting should be preserved
        result = TextInlineFormatter.parse_inline_formatting("** bold with spaces **")
        assert len(result) == 1
        assert result[0].plain_text == " bold with spaces "
        assert result[0].annotations.bold is True