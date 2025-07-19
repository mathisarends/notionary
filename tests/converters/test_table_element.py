import unittest

from notionary.blocks import TableElement


class TestTableElement(unittest.TestCase):

    def setUp(self):
        self.markdown_table = (
            "| Name    | Age | City      |\n"
            "|---------|-----|-----------|\n"
            "| Alice   | 30  | New York  |\n"
            "| Bob     | 25  | Berlin    |"
        )

        self.notion_table = {
            "type": "table",
            "table": {
                "table_width": 3,
                "has_column_header": True,
                "has_row_header": False,
                "children": [
                    {
                        "type": "table_row",
                        "table_row": {
                            "cells": [
                                [{"type": "text", "text": {"content": "Name"}}],
                                [{"type": "text", "text": {"content": "Age"}}],
                                [{"type": "text", "text": {"content": "City"}}],
                            ]
                        },
                    },
                    {
                        "type": "table_row",
                        "table_row": {
                            "cells": [
                                [{"type": "text", "text": {"content": "Alice"}}],
                                [{"type": "text", "text": {"content": "30"}}],
                                [{"type": "text", "text": {"content": "New York"}}],
                            ]
                        },
                    },
                    {
                        "type": "table_row",
                        "table_row": {
                            "cells": [
                                [{"type": "text", "text": {"content": "Bob"}}],
                                [{"type": "text", "text": {"content": "25"}}],
                                [{"type": "text", "text": {"content": "Berlin"}}],
                            ]
                        },
                    },
                ],
            },
            "children": [],  # will be auto-used by `notion_to_markdown`
        }

        # Simulate Notion structure having the same children at the top-level for export
        self.notion_table["children"] = self.notion_table["table"]["children"]

    def test_match_markdown(self):
        self.assertTrue(TableElement.match_markdown(self.markdown_table))
        self.assertFalse(TableElement.match_markdown("Just some text\nAnother line"))

    def test_match_notion(self):
        self.assertTrue(TableElement.match_notion(self.notion_table))
        self.assertFalse(TableElement.match_notion({"type": "paragraph"}))

    def test_markdown_to_notion(self):
        block = TableElement.markdown_to_notion(self.markdown_table)
        self.assertIsNotNone(block)
        self.assertEqual(block["type"], "table")
        self.assertEqual(block["table"]["table_width"], 3)
        self.assertEqual(len(block["table"]["children"]), 3)

    def test_notion_to_markdown(self):
        markdown = TableElement.notion_to_markdown(self.notion_table)
        self.assertIn("| Name", markdown)
        self.assertIn("| Alice", markdown)
        self.assertIn("| Bob", markdown)
        self.assertIn("| -------- | -------- | -------- |", markdown)

    def test_find_matches(self):
        text = "Intro\n\n" "| H1 | H2 |\n" "|----|----|\n" "| A1 | A2 |\n\n" "End"
        matches = TableElement.find_matches(text)
        self.assertEqual(len(matches), 1)
        start, end, block = matches[0]
        self.assertLess(start, end)
        self.assertEqual(block["type"], "table")

    def test_is_multiline(self):
        self.assertTrue(TableElement.is_multiline())

    def test_markdown_to_notion_invalid(self):
        invalid_md = "Not a table\nStill not a table"
        self.assertIsNone(TableElement.markdown_to_notion(invalid_md))

    def test_notion_to_markdown_empty(self):
        empty_table = {
            "type": "table",
            "table": {
                "table_width": 2,
                "has_column_header": True,
                "has_row_header": False,
            },
            "children": [],
        }
        md = TableElement.notion_to_markdown(empty_table)
        self.assertIn("| Column 1 | Column 2 |", md)
        self.assertIn("| -------- | -------- |", md)


if __name__ == "__main__":
    unittest.main()
