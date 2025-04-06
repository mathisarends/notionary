import unittest
from notionary.converters.elements.paragraph_element import ParagraphElement


class TestParagraphElement(unittest.TestCase):

    def test_match_markdown_always_true(self):
        """Paragraph is fallback element, always returns True."""
        self.assertTrue(ParagraphElement.match_markdown("Just some text"))
        self.assertTrue(ParagraphElement.match_markdown(""))  # even empty

    def test_match_notion(self):
        """Correctly matches Notion paragraph block."""
        self.assertTrue(ParagraphElement.match_notion({"type": "paragraph"}))
        self.assertFalse(ParagraphElement.match_notion({"type": "heading_1"}))

    def test_markdown_to_notion(self):
        """Converts markdown paragraph to Notion format."""
        text = "This is a paragraph with *some* **formatting**."
        block = ParagraphElement.markdown_to_notion(text)
        self.assertEqual(block["type"], "paragraph")
        self.assertIn("rich_text", block["paragraph"])
        self.assertGreater(len(block["paragraph"]["rich_text"]), 0)

    def test_markdown_to_notion_empty(self):
        """Returns None for empty or whitespace-only markdown."""
        self.assertIsNone(ParagraphElement.markdown_to_notion(""))
        self.assertIsNone(ParagraphElement.markdown_to_notion("   "))

    def test_notion_to_markdown(self):
        """Converts Notion paragraph block to markdown string."""
        block = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Some paragraph content"}}
                ]
            },
        }
        md = ParagraphElement.notion_to_markdown(block)
        self.assertEqual(md, "Some paragraph content")

    def test_notion_to_markdown_empty(self):
        """Returns None for paragraph blocks without content."""
        block = {"type": "paragraph", "paragraph": {"rich_text": []}}
        self.assertIsNone(ParagraphElement.notion_to_markdown(block))

    def test_notion_to_markdown_wrong_type(self):
        """Returns None if the block is not a paragraph."""
        self.assertIsNone(ParagraphElement.notion_to_markdown({"type": "heading_2"}))


if __name__ == "__main__":
    unittest.main()
