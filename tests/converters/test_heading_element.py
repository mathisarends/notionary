import unittest

from notionary.core.converters.elements.heading_element import HeadingElement


class TestHeadingElement(unittest.TestCase):

    def test_match_markdown(self):
        """Test matching of valid and invalid markdown headings."""
        self.assertTrue(HeadingElement.match_markdown("# Heading 1"))
        self.assertTrue(HeadingElement.match_markdown("### Heading 3"))
        self.assertTrue(HeadingElement.match_markdown("###### Heading 6"))
        self.assertFalse(HeadingElement.match_markdown("####### Too many hashes"))
        self.assertFalse(HeadingElement.match_markdown("No heading here"))

    def test_match_notion(self):
        """Test matching of Notion heading blocks."""
        self.assertTrue(HeadingElement.match_notion({"type": "heading_1"}))
        self.assertTrue(HeadingElement.match_notion({"type": "heading_3"}))
        self.assertFalse(HeadingElement.match_notion({"type": "paragraph"}))
        self.assertFalse(HeadingElement.match_notion({"type": "heading_7"}))
        self.assertFalse(HeadingElement.match_notion({"type": "heading_"}))

    def test_markdown_to_notion(self):
        """Test conversion from markdown heading to Notion heading block."""
        md = "## Subtitle"
        block = HeadingElement.markdown_to_notion(md)
        self.assertIsNotNone(block)
        self.assertEqual(block["type"], "heading_2")
        self.assertEqual(block["heading_2"]["rich_text"][0]["type"], "text")
        self.assertEqual(
            block["heading_2"]["rich_text"][0]["text"]["content"], "Subtitle"
        )

    def test_markdown_to_notion_invalid(self):
        """Invalid markdown should return None."""
        self.assertIsNone(HeadingElement.markdown_to_notion("Just a paragraph"))

    def test_notion_to_markdown(self):
        """Test conversion from Notion heading block to markdown."""
        block = {
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"type": "text", "text": {"content": "Section Title"}}]
            },
        }
        md = HeadingElement.notion_to_markdown(block)
        self.assertEqual(md, "### Section Title")

    def test_notion_to_markdown_invalid(self):
        """Invalid Notion block should return None."""
        self.assertIsNone(HeadingElement.notion_to_markdown({"type": "paragraph"}))
        self.assertIsNone(HeadingElement.notion_to_markdown({"type": "heading_x"}))

    def test_heading_with_formatting(self):
        """Test markdown to Notion and back with inline formatting (e.g. bold)."""
        md = "### This is **important**"
        block = HeadingElement.markdown_to_notion(md)
        self.assertEqual(block["type"], "heading_3")
        back_md = HeadingElement.notion_to_markdown(block)
        self.assertIn("important", back_md)
        self.assertTrue(back_md.startswith("###"))


if __name__ == "__main__":
    unittest.main()
