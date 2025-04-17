import unittest

from notionary.elements.list_element import NumberedListElement


class TestNumberedListElement(unittest.TestCase):

    def test_match_markdown(self):
        self.assertTrue(NumberedListElement.match_markdown("1. First item"))
        self.assertTrue(NumberedListElement.match_markdown("42. Item number 42"))
        self.assertFalse(NumberedListElement.match_markdown("- Not numbered"))
        self.assertFalse(NumberedListElement.match_markdown("No list here"))

    def test_match_notion(self):
        self.assertTrue(
            NumberedListElement.match_notion({"type": "numbered_list_item"})
        )
        self.assertFalse(NumberedListElement.match_notion({"type": "heading_1"}))

    def test_markdown_to_notion(self):
        md = "1. Numbered item"
        block = NumberedListElement.markdown_to_notion(md)
        self.assertIsNotNone(block)
        self.assertEqual(block["type"], "numbered_list_item")
        self.assertEqual(
            block["numbered_list_item"]["rich_text"][0]["text"]["content"],
            "Numbered item",
        )

    def test_notion_to_markdown(self):
        block = {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Second item"}}],
                "color": "default",
            },
        }
        md = NumberedListElement.notion_to_markdown(block)
        self.assertEqual(md, "1. Second item")  # always "1." in markdown

    def test_is_multiline(self):
        self.assertFalse(NumberedListElement.is_multiline())


if __name__ == "__main__":
    unittest.main()
