import unittest

from notionary.elements.divider_element import DividerElement


class TestDividerElement(unittest.TestCase):

    def test_match_markdown(self):
        """Test that markdown dividers are correctly identified."""
        self.assertTrue(DividerElement.match_markdown("---"))
        self.assertTrue(DividerElement.match_markdown("----"))
        self.assertTrue(DividerElement.match_markdown("   ---   "))
        self.assertFalse(DividerElement.match_markdown("- - -"))
        self.assertFalse(DividerElement.match_markdown("--"))
        self.assertFalse(DividerElement.match_markdown("text---text"))

    def test_match_notion(self):
        """Test that Notion divider blocks are correctly identified."""
        self.assertTrue(DividerElement.match_notion({"type": "divider"}))
        self.assertFalse(DividerElement.match_notion({"type": "paragraph"}))

    def test_markdown_to_notion(self):
        """Test conversion from markdown to Notion format."""
        expected = {"type": "divider", "divider": {}}

        # Valid divider
        self.assertEqual(DividerElement.markdown_to_notion("---"), expected)
        self.assertEqual(DividerElement.markdown_to_notion("  -----  "), expected)

        # Invalid divider
        self.assertIsNone(DividerElement.markdown_to_notion("not a divider"))
        self.assertIsNone(DividerElement.markdown_to_notion("--"))

    def test_notion_to_markdown(self):
        """Test conversion from Notion format to markdown."""
        # Valid divider block
        self.assertEqual(DividerElement.notion_to_markdown({"type": "divider"}), "---")

        # Invalid divider block
        self.assertIsNone(DividerElement.notion_to_markdown({"type": "paragraph"}))

    def test_is_multiline(self):
        """Test that dividers are not multiline elements."""
        self.assertFalse(DividerElement.is_multiline())


if __name__ == "__main__":
    unittest.main()
