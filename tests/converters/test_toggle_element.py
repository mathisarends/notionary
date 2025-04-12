import unittest

from notionary.core.converters.elements.toggle_element import ToggleElement

class TestToggleElement(unittest.TestCase):

    def test_match_markdown(self):
        """Test that toggle markdown lines are correctly matched."""
        self.assertTrue(ToggleElement.match_markdown("+++ This is a toggle"))
        self.assertTrue(ToggleElement.match_markdown("+++   Another one"))
        self.assertFalse(ToggleElement.match_markdown("++ Not a toggle"))
        self.assertFalse(ToggleElement.match_markdown("> Blockquote"))
        self.assertFalse(ToggleElement.match_markdown("+++"))

    def test_match_notion(self):
        """Test that Notion toggle blocks are correctly identified."""
        self.assertTrue(ToggleElement.match_notion({"type": "toggle"}))
        self.assertFalse(ToggleElement.match_notion({"type": "paragraph"}))

    def test_markdown_to_notion(self):
        """Test markdown toggle conversion to Notion block."""
        markdown = "+++ My Toggle Title"
        expected = {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "My Toggle Title"}}],
                "color": "default",
                "children": [],
            },
        }
        self.assertEqual(ToggleElement.markdown_to_notion(markdown), expected)

        # Invalid toggle (no title)
        self.assertIsNone(ToggleElement.markdown_to_notion("+++"))
        self.assertIsNone(ToggleElement.markdown_to_notion("This is just text"))

    def test_notion_to_markdown(self):
        """Test Notion toggle block conversion to markdown."""
        notion_block = {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "My Toggle Title"}}],
                "color": "default",
                "children": [],
            },
        }
        self.assertEqual(
            ToggleElement.notion_to_markdown(notion_block), "+++ My Toggle Title"
        )

        # With mocked children (will render placeholders)
        notion_with_children = {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "Parent"}}],
                "color": "default",
                "children": [{"type": "paragraph", "paragraph": {"rich_text": []}}],
            },
        }
        self.assertEqual(
            ToggleElement.notion_to_markdown(notion_with_children),
            "+++ Parent\n    [Nested content]",
        )

        # Invalid block
        self.assertIsNone(ToggleElement.notion_to_markdown({"type": "paragraph"}))

    def test_is_multiline(self):
        """Test that toggle elements are multiline."""
        self.assertTrue(ToggleElement.is_multiline())


if __name__ == "__main__":
    unittest.main()
