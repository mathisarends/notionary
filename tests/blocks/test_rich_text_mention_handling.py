from unittest.mock import AsyncMock, MagicMock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.rich_text.rich_text_models import MentionType, RichTextType


class TestMentionHandling:
    """Test mention-specific functionality in converters."""

    @pytest.mark.asyncio
    async def test_page_mention_conversion(self):
        """Test page mention handling."""
        # Mock the mention resolver
        mock_resolver = AsyncMock()
        mock_resolver.resolve_mention_from_markdown.return_value = MagicMock(
            type=RichTextType.MENTION, mention=MagicMock(type=MentionType.PAGE, page=MagicMock(id="page-123"))
        )

        converter = MarkdownRichTextConverter()
        converter.mention_resolver = mock_resolver

        await converter.to_rich_text("Check @page-name")

        # Should call the mention resolver
        mock_resolver.resolve_mention_from_markdown.assert_called()

    @pytest.mark.asyncio
    async def test_database_mention_conversion(self):
        """Test database mention handling."""
        mock_resolver = AsyncMock()
        mock_resolver.resolve_mention_from_markdown.return_value = MagicMock(
            type=RichTextType.MENTION, mention=MagicMock(type=MentionType.DATABASE, database=MagicMock(id="db-123"))
        )

        converter = MarkdownRichTextConverter()
        converter.mention_resolver = mock_resolver

        await converter.to_rich_text("Check @database-name")

        # Should call the mention resolver
        mock_resolver.resolve_mention_from_markdown.assert_called()

    @pytest.mark.asyncio
    async def test_user_mention_conversion(self):
        """Test user mention handling."""
        mock_resolver = AsyncMock()
        mock_resolver.resolve_mention_from_markdown.return_value = MagicMock(
            type=RichTextType.MENTION, mention=MagicMock(type=MentionType.USER, user=MagicMock(id="user-123"))
        )

        converter = MarkdownRichTextConverter()
        converter.mention_resolver = mock_resolver

        await converter.to_rich_text("Ask @username")

        # Should call the mention resolver
        mock_resolver.resolve_mention_from_markdown.assert_called()

    @pytest.mark.asyncio
    async def test_mention_to_markdown_page(self):
        """Test converting page mention to markdown."""
        converter = RichTextToMarkdownConverter()

        # Create a page mention manually
        from notionary.blocks.rich_text.rich_text_models import Mention, RichTextObject

        mention = Mention(type=MentionType.PAGE, page=MagicMock(id="page-123"))
        rich_text = [RichTextObject(type=RichTextType.MENTION, mention=mention, plain_text="@page-name")]

        result = await converter.to_markdown(rich_text)
        assert "@page-name" in result

    @pytest.mark.asyncio
    async def test_mention_to_markdown_database(self):
        """Test converting database mention to markdown."""
        converter = RichTextToMarkdownConverter()

        from notionary.blocks.rich_text.rich_text_models import Mention, RichTextObject

        mention = Mention(type=MentionType.DATABASE, database=MagicMock(id="db-123"))
        rich_text = [RichTextObject(type=RichTextType.MENTION, mention=mention, plain_text="@database-name")]

        result = await converter.to_markdown(rich_text)
        assert "@database-name" in result

    @pytest.mark.asyncio
    async def test_mention_to_markdown_user(self):
        """Test converting user mention to markdown."""
        converter = RichTextToMarkdownConverter()

        from notionary.blocks.rich_text.rich_text_models import Mention, RichTextObject

        mention = Mention(type=MentionType.USER, user=MagicMock(id="user-123"))
        rich_text = [RichTextObject(type=RichTextType.MENTION, mention=mention, plain_text="@username")]

        result = await converter.to_markdown(rich_text)
        assert "@username" in result

    @pytest.mark.asyncio
    async def test_mixed_mentions_and_formatting(self):
        """Test mixing mentions with other formatting."""
        mock_resolver = AsyncMock()
        mock_resolver.resolve_mention_from_markdown.return_value = MagicMock(
            type=RichTextType.MENTION, mention=MagicMock(type=MentionType.PAGE, page=MagicMock(id="page-123"))
        )

        converter = MarkdownRichTextConverter()
        converter.mention_resolver = mock_resolver

        # Should handle both mentions and formatting
        result = await converter.to_rich_text("**Important**: Ask @username about @page-name")

        # Should process both formatting and mentions
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_mention_fallback_when_not_resolved(self):
        """Test fallback when mention cannot be resolved."""
        mock_resolver = AsyncMock()
        mock_resolver.resolve_mention_from_markdown.return_value = None  # No resolution

        converter = MarkdownRichTextConverter()
        converter.mention_resolver = mock_resolver

        result = await converter.to_rich_text("Check @unknown-reference")

        # Should fallback to plain text
        assert len(result) >= 1
        assert any("@unknown-reference" in obj.plain_text for obj in result)


class TestConverterIntegration:
    """Test integration between converters and other components."""

    @pytest.mark.asyncio
    async def test_converter_without_mention_resolver(self):
        """Test converter behavior without mention resolver."""
        converter = MarkdownRichTextConverter()
        # No mention resolver set

        result = await converter.to_rich_text("Check @page-name")

        # Should handle gracefully, treating as plain text
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_converter_with_custom_patterns(self):
        """Test converter with custom formatting patterns."""
        converter = MarkdownRichTextConverter()

        # Test with complex patterns
        result = await converter.to_rich_text("**bold** *italic* `code` [link](url)")

        # Should handle all patterns
        assert len(result) >= 4  # At least one for each format

    @pytest.mark.asyncio
    async def test_error_handling_invalid_markdown(self):
        """Test error handling with malformed markdown."""
        converter = MarkdownRichTextConverter()

        # Malformed markdown should not crash
        result = await converter.to_rich_text("**unclosed bold")

        # Should handle gracefully
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_error_handling_invalid_rich_text(self):
        """Test error handling with invalid rich text."""
        converter = RichTextToMarkdownConverter()

        # Invalid rich text object
        result = await converter.to_markdown([None])

        # Should handle gracefully
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_performance_large_text(self):
        """Test performance with large text blocks."""
        converter = MarkdownRichTextConverter()

        # Large text with multiple formatting
        large_text = "**Bold** " * 1000 + "*Italic* " * 1000

        result = await converter.to_rich_text(large_text)

        # Should handle large text efficiently
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test memory efficiency with repeated conversions."""
        markdown_converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        # Multiple conversions should not leak memory
        for _ in range(100):
            rich_objects = await markdown_converter.to_rich_text("**test**")
            markdown = await rich_text_converter.to_markdown(rich_objects)

        # Should complete without issues
        assert markdown == "**test**"


class TestSpecialFormatting:
    """Test special formatting cases and edge conditions."""

    @pytest.mark.asyncio
    async def test_escaped_formatting(self):
        """Test handling of escaped formatting characters."""
        converter = MarkdownRichTextConverter()

        # Escaped characters should be treated as literal
        result = await converter.to_rich_text(r"\*not bold\*")

        # Should handle escaped characters
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_multiple_consecutive_formatting(self):
        """Test multiple consecutive formatting markers."""
        converter = MarkdownRichTextConverter()

        result = await converter.to_rich_text("**bold1** **bold2**")

        # Should handle multiple bold sections
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_formatting_at_boundaries(self):
        """Test formatting at text boundaries."""
        converter = MarkdownRichTextConverter()

        result = await converter.to_rich_text("**start** middle **end**")

        # Should handle formatting at boundaries
        assert len(result) >= 3

    @pytest.mark.asyncio
    async def test_overlapping_formatting(self):
        """Test overlapping formatting patterns."""
        converter = MarkdownRichTextConverter()

        # This is tricky markdown - implementation dependent
        result = await converter.to_rich_text("**bold *and italic** still italic*")

        # Should handle overlapping gracefully
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_color_background_combinations(self):
        """Test color and background color combinations."""
        converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        markdown = "(red_background:highlighted)"

        rich_objects = await converter.to_rich_text(markdown)
        back_to_markdown = await rich_text_converter.to_markdown(rich_objects)

        assert "(red_background:highlighted)" in back_to_markdown

    @pytest.mark.asyncio
    async def test_equation_with_special_chars(self):
        """Test equations with special mathematical characters."""
        converter = MarkdownRichTextConverter()
        rich_text_converter = RichTextToMarkdownConverter()

        markdown = "$\\int_{0}^{\\infty} e^{-x} dx = 1$"

        rich_objects = await converter.to_rich_text(markdown)
        back_to_markdown = await rich_text_converter.to_markdown(rich_objects)

        # Should preserve mathematical notation
        assert "\\int" in back_to_markdown
        assert "\\infty" in back_to_markdown
