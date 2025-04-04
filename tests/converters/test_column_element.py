import unittest
from unittest.mock import patch

from notionary.converters.elements.column_element import ColumnElement


class TestColumnElement(unittest.TestCase):

    def test_match_markdown(self):
        """Test matching the ::: columns start marker."""
        self.assertTrue(ColumnElement.match_markdown("::: columns"))
        self.assertFalse(ColumnElement.match_markdown("::: column"))
        self.assertFalse(ColumnElement.match_markdown("::: something else"))

    def test_match_notion(self):
        """Test Notion column_list block matching."""
        self.assertTrue(ColumnElement.match_notion({"type": "column_list"}))
        self.assertFalse(ColumnElement.match_notion({"type": "paragraph"}))

    def test_markdown_to_notion(self):
        """Test basic column block creation from markdown."""
        result = ColumnElement.markdown_to_notion("::: columns")
        expected = {
            "type": "column_list",
            "column_list": {
                "children": []
            }
        }
        self.assertEqual(result, expected)

        self.assertIsNone(ColumnElement.markdown_to_notion("::: column"))
        self.assertIsNone(ColumnElement.markdown_to_notion("some other text"))

    def test_notion_to_markdown(self):
        """Test conversion from column_list block to markdown."""
        notion_block = {
            "type": "column_list",
            "column_list": {
                "children": [
                    {
                        "type": "column",
                        "column": {
                            "children": [
                                {"type": "paragraph"}
                            ]
                        }
                    },
                    {
                        "type": "column",
                        "column": {
                            "children": [
                                {"type": "paragraph"}
                            ]
                        }
                    }
                ]
            }
        }

        markdown = ColumnElement.notion_to_markdown(notion_block)
        expected = (
            "::: columns\n"
            "::: column\n"
            "  [Column content]\n"
            ":::\n"
            "::: column\n"
            "  [Column content]\n"
            ":::\n"
            ":::"
        )
        self.assertEqual(markdown, expected)

    @patch("notionary.converters.elements.column_element.MarkdownToNotionConverter")
    def test_find_matches(self, MockConverter):
        """Test that column blocks are found and parsed correctly."""
        # Mock converter.convert to always return a simple block
        mock_converter_instance = MockConverter.return_value
        mock_converter_instance.convert.return_value = [{"type": "paragraph", "paragraph": {"rich_text": []}}]

        markdown = (
            "::: columns\n"
            "::: column\n"
            "Hello from column 1\n"
            ":::\n"
            "::: column\n"
            "Hello from column 2\n"
            ":::\n"
            ":::"
        )

        matches = ColumnElement.find_matches(markdown)
        self.assertEqual(len(matches), 1)
        start_pos, end_pos, block = matches[0]

        self.assertEqual(block["type"], "column_list")
        self.assertIn("children", block["column_list"])
        self.assertEqual(len(block["column_list"]["children"]), 2)
        self.assertEqual(block["column_list"]["children"][0]["type"], "column")
        self.assertEqual(block["column_list"]["children"][1]["type"], "column")


if __name__ == "__main__":
    unittest.main()
