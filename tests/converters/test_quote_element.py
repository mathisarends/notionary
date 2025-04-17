import unittest
from notionary.elements.qoute_element import QuoteElement


class TestQuoteElement(unittest.TestCase):

    def test_match_markdown(self):
        """Test detection of blockquotes in markdown."""
        self.assertTrue(QuoteElement.match_markdown("> A simple quote"))
        self.assertTrue(
            QuoteElement.match_markdown("> [background:blue] Colored quote")
        )
        self.assertFalse(QuoteElement.match_markdown("No quote here"))

    def test_match_notion(self):
        """Test detection of Notion quote blocks."""
        self.assertTrue(QuoteElement.match_notion({"type": "quote"}))
        self.assertFalse(QuoteElement.match_notion({"type": "paragraph"}))

    def test_markdown_to_notion_default_color(self):
        """Convert basic markdown quote to Notion block with default color."""
        md = "> This is a test quote"
        block = QuoteElement.markdown_to_notion(md)
        self.assertEqual(block["type"], "quote")
        self.assertEqual(block["quote"]["color"], "default")
        self.assertEqual(
            block["quote"]["rich_text"][0]["text"]["content"], "This is a test quote"
        )

    def test_markdown_to_notion_with_color(self):
        """Convert markdown quote with background color to Notion block."""
        md = "> [background:blue] This is a blue quote"
        block = QuoteElement.markdown_to_notion(md)
        self.assertEqual(block["quote"]["color"], "blue_background")
        self.assertEqual(
            block["quote"]["rich_text"][0]["text"]["content"], "This is a blue quote"
        )

    def test_notion_to_markdown_default(self):
        """Convert Notion quote block back to simple markdown."""
        block = {
            "type": "quote",
            "quote": {
                "rich_text": [{"type": "text", "text": {"content": "Markdown again"}}],
                "color": "default",
            },
        }
        md = QuoteElement.notion_to_markdown(block)
        self.assertEqual(md, "> Markdown again")

    def test_notion_to_markdown_with_color(self):
        """Convert colored Notion quote block back to markdown with color tag."""
        block = {
            "type": "quote",
            "quote": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Colorful content"}}
                ],
                "color": "green_background",
            },
        }
        md = QuoteElement.notion_to_markdown(block)
        self.assertTrue(md.startswith("> [background:green] Colorful content"))

    def test_multiline_quote(self):
        """Check multiline blockquote handling."""
        md = "> Line one\n> Line two\n> Line three"
        block = QuoteElement.markdown_to_notion(md)
        self.assertIn(
            "Line one\nLine two\nLine three",
            block["quote"]["rich_text"][0]["text"]["content"],
        )

    def test_find_matches(self):
        """Test finding multiple quote matches in a mixed markdown text."""
        text = """
Some intro text

> Quote one line

More text

> [background:red] First line of colored quote
> Second line of same quote
"""
        matches = QuoteElement.find_matches(text)
        self.assertEqual(len(matches), 2)
        self.assertIn(
            "Quote one line", matches[0][2]["quote"]["rich_text"][0]["text"]["content"]
        )
        self.assertEqual(matches[1][2]["quote"]["color"], "red_background")

    def test_is_multiline(self):
        """Blockquotes should be multiline."""
        self.assertTrue(QuoteElement.is_multiline())


if __name__ == "__main__":
    unittest.main()
