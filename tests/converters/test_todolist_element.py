import unittest

from notionary.elements.text_inline_formatter import TextInlineFormatter
from notionary.elements.todo_lists import TodoElement


class TestTodoElement(unittest.TestCase):

    def test_match_markdown(self):
        """Test that markdown todo items are correctly identified."""
        # Unchecked todos with different list markers
        self.assertTrue(TodoElement.match_markdown("- [ ] Unchecked todo"))
        self.assertTrue(TodoElement.match_markdown("* [ ] Unchecked todo"))
        self.assertTrue(TodoElement.match_markdown("+ [ ] Unchecked todo"))
        self.assertTrue(TodoElement.match_markdown("  - [ ] Indented todo"))

        # Checked todos
        self.assertTrue(TodoElement.match_markdown("- [x] Checked todo"))
        self.assertTrue(TodoElement.match_markdown("* [x] Checked todo"))
        self.assertTrue(TodoElement.match_markdown("+ [x] Checked todo"))

        # Invalid formats
        self.assertFalse(TodoElement.match_markdown("- Regular list item"))
        self.assertFalse(TodoElement.match_markdown("[ ] Not a todo"))
        self.assertFalse(TodoElement.match_markdown("- [o] Invalid checkbox"))

    def test_match_notion(self):
        """Test that Notion to_do blocks are correctly identified."""
        self.assertTrue(TodoElement.match_notion({"type": "to_do"}))
        self.assertFalse(TodoElement.match_notion({"type": "paragraph"}))
        self.assertFalse(TodoElement.match_notion({"type": "bulleted_list_item"}))

    def test_markdown_to_notion(self):
        """Test conversion from markdown to Notion format."""
        # Unchecked todo
        unchecked_todo = "- [ ] Buy groceries"
        notion_block = TodoElement.markdown_to_notion(unchecked_todo)

        self.assertEqual(notion_block["type"], "to_do")
        self.assertEqual(notion_block["to_do"]["checked"], False)
        self.assertEqual(notion_block["to_do"]["color"], "default")

        rich_text = notion_block["to_do"]["rich_text"]
        extracted_text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        self.assertEqual(extracted_text, "Buy groceries")

        # Checked todo
        checked_todo = "- [x] Complete assignment"
        notion_block = TodoElement.markdown_to_notion(checked_todo)

        self.assertEqual(notion_block["type"], "to_do")
        self.assertEqual(notion_block["to_do"]["checked"], True)

        rich_text = notion_block["to_do"]["rich_text"]
        extracted_text = TextInlineFormatter.extract_text_with_formatting(rich_text)
        self.assertEqual(extracted_text, "Complete assignment")

        # Invalid todo format
        self.assertIsNone(TodoElement.markdown_to_notion("- Regular list item"))

    def test_notion_to_markdown(self):
        """Test conversion from Notion format to markdown."""
        # Create a Notion block using the implementation's function
        notion_block = TodoElement._create_todo_block("Buy groceries", False)
        markdown = TodoElement.notion_to_markdown(notion_block)
        self.assertEqual(markdown, "- [ ] Buy groceries")

        # Checked todo
        notion_block = TodoElement._create_todo_block("Complete assignment", True)
        markdown = TodoElement.notion_to_markdown(notion_block)
        self.assertEqual(markdown, "- [x] Complete assignment")

        # Invalid block type
        self.assertIsNone(TodoElement.notion_to_markdown({"type": "paragraph"}))

    def test_with_formatting(self):
        """Test that formatting is preserved during conversion."""
        todo_with_formatting = "- [ ] Remember to *buy* **groceries**"
        notion_block = TodoElement.markdown_to_notion(todo_with_formatting)

        # Convert back to markdown
        markdown = TodoElement.notion_to_markdown(notion_block)

        # The exact formatting might depend on the implementation of parse_inline_formatting
        # and extract_text_with_formatting, but the basic content should be preserved
        self.assertIn("Remember to", markdown)
        self.assertIn("buy", markdown)
        self.assertIn("groceries", markdown)
        self.assertTrue(markdown.startswith("- [ ] "))

    def test_is_multiline(self):
        """Test that todos are not multiline elements."""
        self.assertFalse(TodoElement.is_multiline())


if __name__ == "__main__":
    unittest.main()
