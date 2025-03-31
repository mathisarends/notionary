import unittest
from unittest.mock import patch

from notionary.core.notion_content_converter import NotionContentConverter

class TestNotionContentConverter(unittest.TestCase):
    """Tests for the NotionContentConverter class."""

    def test_extract_text_from_rich_text(self):
        """Test extracting text from rich_text format."""
        rich_text = [
            {"plain_text": "Hello"},
            {"plain_text": " "},
            {"plain_text": "World"}
        ]
        
        result = NotionContentConverter._extract_text_from_rich_text(rich_text)
        self.assertEqual(result, "Hello World")
        
        self.assertEqual(NotionContentConverter._extract_text_from_rich_text([]), "")
        
        rich_text_missing_key = [{"other_key": "value"}]
        self.assertEqual(NotionContentConverter._extract_text_from_rich_text(rich_text_missing_key), "")

    @patch('notionary.core.notion_markdown_parser.NotionMarkdownParser.parse_markdown')
    def test_markdown_to_blocks(self, mock_parse_markdown):
        """Test converting markdown to Notion blocks."""
        mock_blocks = [{"type": "paragraph", "paragraph": {"rich_text": []}}]
        mock_parse_markdown.return_value = mock_blocks
        
        result = NotionContentConverter.markdown_to_blocks("Some markdown")
        
        mock_parse_markdown.assert_called_once_with("Some markdown")
        self.assertEqual(result, mock_blocks)

    def test_blocks_to_text_empty_blocks(self):
        """Test converting empty blocks list to text."""
        self.assertEqual(NotionContentConverter.blocks_to_text([]), "Keine Inhalte gefunden.")

    def test_blocks_to_text_paragraph(self):
        """Test converting paragraph blocks to text."""
        blocks = [{
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"plain_text": "This is a paragraph."}
                ]
            }
        }]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        self.assertEqual(result, "This is a paragraph.")

    def test_blocks_to_text_headings(self):
        """Test converting heading blocks to text."""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "Heading 1"}]
                }
            },
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"plain_text": "Heading 2"}]
                }
            },
            {
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"plain_text": "Heading 3"}]
                }
            }
        ]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        expected = "# Heading 1\n\n## Heading 2\n\n### Heading 3"
        self.assertEqual(result, expected)

    def test_blocks_to_text_list_items(self):
        """Test converting list item blocks to text."""
        blocks = [
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"plain_text": "Bullet point"}]
                }
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"plain_text": "Numbered point"}]
                }
            }
        ]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        expected = "• Bullet point\n\n1. Numbered point"
        self.assertEqual(result, expected)

    def test_blocks_to_text_divider(self):
        """Test converting divider block to text."""
        blocks = [{"type": "divider"}]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        self.assertEqual(result, "---")

    def test_blocks_to_text_code(self):
        """Test converting code block to text."""
        blocks = [{
            "type": "code",
            "code": {
                "rich_text": [{"plain_text": "def hello():\n    print('world')"}],
                "language": "python"
            }
        }]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        expected = "```python\ndef hello():\n    print('world')\n```"
        self.assertEqual(result, expected)

    def test_blocks_to_text_mixed_content(self):
        """Test converting a mix of block types to text."""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "My Document"}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "This is an introduction paragraph."}]
                }
            },
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"plain_text": "Section 1"}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"plain_text": "First point"}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"plain_text": "Second point"}]
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "code",
                "code": {
                    "rich_text": [{"plain_text": "print('Hello world')"}],
                    "language": "python"
                }
            }
        ]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        expected = (
            "# My Document\n\n"
            "This is an introduction paragraph.\n\n"
            "## Section 1\n\n"
            "• First point\n\n"
            "• Second point\n\n"
            "---\n\n"
            "```python\nprint('Hello world')\n```"
        )
        self.assertEqual(result, expected)

    def test_blocks_to_text_unknown_block_type(self):
        """Test handling of unknown block types."""
        blocks = [
            {"type": "unknown_type", "unknown_type": {"rich_text": [{"plain_text": "Some text"}]}}
        ]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        self.assertEqual(result, "")

    def test_blocks_to_text_missing_rich_text(self):
        """Test handling blocks with missing rich_text field."""
        blocks = [
            {"type": "paragraph", "paragraph": {}}
        ]
        
        result = NotionContentConverter.blocks_to_text(blocks)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()