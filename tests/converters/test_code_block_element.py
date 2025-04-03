import unittest
from notionary.converters.elements.code_blocks import CodeBlockElement

class TestCodeBlockElement(unittest.TestCase):

    def test_match_markdown(self):
        """Should match code block markdown syntax."""
        self.assertTrue(CodeBlockElement.match_markdown("```python\nprint('Hello')\n```"))
        self.assertTrue(CodeBlockElement.match_markdown("```js\nconsole.log('hi');\n```"))
        self.assertFalse(CodeBlockElement.match_markdown("This is just text."))

    def test_match_notion(self):
        """Should match Notion code block."""
        self.assertTrue(CodeBlockElement.match_notion({"type": "code"}))
        self.assertFalse(CodeBlockElement.match_notion({"type": "paragraph"}))

    def test_markdown_to_notion(self):
        """Convert markdown code block to Notion format."""
        md = "```python\nprint('Hello')\n```"
        block = CodeBlockElement.markdown_to_notion(md)
        self.assertEqual(block["type"], "code")
        self.assertEqual(block["code"]["language"], "python")
        self.assertEqual(block["code"]["rich_text"][0]["text"]["content"], "print('Hello')")

    def test_markdown_to_notion_no_language(self):
        """Convert markdown code block without language to Notion format."""
        md = "```\njust some code\n```"
        block = CodeBlockElement.markdown_to_notion(md)
        self.assertEqual(block["code"]["language"], "plain text")
        self.assertEqual(block["code"]["rich_text"][0]["text"]["content"], "just some code")

    def test_notion_to_markdown(self):
        """Convert Notion code block to markdown format."""
        block = {
            "type": "code",
            "code": {
                "language": "python",
                "rich_text": [
                    {
                        "plain_text": "print('Hi')",
                        "type": "text",
                        "text": {"content": "print('Hi')"},
                        "annotations": {
                            "bold": False, "italic": False,
                            "strikethrough": False, "underline": False,
                            "code": False, "color": "default"
                        }
                    }
                ]
            }
        }
        md = CodeBlockElement.notion_to_markdown(block)
        self.assertEqual(md, "```python\nprint('Hi')\n```")

    def test_find_matches(self):
        """Extract all code blocks from markdown."""
        text = (
            "Intro\n\n"
            "```python\n"
            "print('Hello')\n"
            "```\n\n"
            "Some more text\n\n"
            "```js\n"
            "console.log('Hi');\n"
            "```"
        )
        matches = CodeBlockElement.find_matches(text)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0][2]["code"]["language"], "python")
        self.assertEqual(matches[1][2]["code"]["language"], "js")
        self.assertIn("print('Hello')", matches[0][2]["code"]["rich_text"][0]["text"]["content"])

    def test_is_multiline(self):
        self.assertTrue(CodeBlockElement.is_multiline())

if __name__ == "__main__":
    unittest.main()
