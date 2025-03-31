import unittest
from typing import Dict, Any

from notionary.core.notion_content_converter import (
    NotionContentConverter,
    ParagraphConverter,
    HeadingConverter,
    BulletedListItemConverter,
    NumberedListItemConverter,
    DividerConverter,
    CodeConverter,
    BlockConverter
)

class TestBlockConverters(unittest.TestCase):
    """Tests für die einzelnen BlockConverter-Implementierungen."""
    
    def test_paragraph_converter(self):
        """Test für den ParagraphConverter."""
        converter = ParagraphConverter()
        
        # Test mit normalem Inhalt
        block = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"plain_text": "Dies ist ein Absatz."}
                ]
            }
        }
        self.assertEqual(converter.convert(block), "Dies ist ein Absatz.")
        
        # Test mit leerem rich_text
        block = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": []
            }
        }
        self.assertIsNone(converter.convert(block))
        
        # Test mit fehlendem rich_text
        block = {
            "type": "paragraph",
            "paragraph": {}
        }
        self.assertIsNone(converter.convert(block))
        
        # Test mit fehlendem paragraph
        block = {
            "type": "paragraph"
        }
        self.assertIsNone(converter.convert(block))
    
    def test_heading_converter(self):
        """Test für den HeadingConverter."""
        # Test für Heading 1
        h1_converter = HeadingConverter(1)
        block = {
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {"plain_text": "Überschrift 1"}
                ]
            }
        }
        self.assertEqual(h1_converter.convert(block), "# Überschrift 1")
        
        # Test für Heading 2
        h2_converter = HeadingConverter(2)
        block = {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {"plain_text": "Überschrift 2"}
                ]
            }
        }
        self.assertEqual(h2_converter.convert(block), "## Überschrift 2")
        
        # Test für Heading 3
        h3_converter = HeadingConverter(3)
        block = {
            "type": "heading_3",
            "heading_3": {
                "rich_text": [
                    {"plain_text": "Überschrift 3"}
                ]
            }
        }
        self.assertEqual(h3_converter.convert(block), "### Überschrift 3")
        
        # Test mit leerem rich_text
        block = {
            "type": "heading_1",
            "heading_1": {
                "rich_text": []
            }
        }
        self.assertIsNone(h1_converter.convert(block))
    
    def test_bulleted_list_item_converter(self):
        """Test für den BulletedListItemConverter."""
        converter = BulletedListItemConverter()
        
        # Test mit normalem Inhalt
        block = {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"plain_text": "Aufzählungspunkt"}
                ]
            }
        }
        self.assertEqual(converter.convert(block), "• Aufzählungspunkt")
        
        # Test mit leerem rich_text
        block = {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": []
            }
        }
        self.assertIsNone(converter.convert(block))
    
    def test_numbered_list_item_converter(self):
        """Test für den NumberedListItemConverter."""
        converter = NumberedListItemConverter()
        
        # Test mit normalem Inhalt
        block = {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": [
                    {"plain_text": "Nummerierter Punkt"}
                ]
            }
        }
        self.assertEqual(converter.convert(block), "1. Nummerierter Punkt")
        
        # Test mit leerem rich_text
        block = {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": []
            }
        }
        self.assertIsNone(converter.convert(block))
    
    def test_divider_converter(self):
        """Test für den DividerConverter."""
        converter = DividerConverter()
        
        # Test mit normalem Block
        block = {"type": "divider"}
        self.assertEqual(converter.convert(block), "---")
        
        # Test mit leerem Block
        block = {}
        self.assertEqual(converter.convert(block), "---")
    
    def test_code_converter(self):
        """Test für den CodeConverter."""
        converter = CodeConverter()
        
        # Test mit normalem Inhalt und Sprache
        block = {
            "type": "code",
            "code": {
                "rich_text": [
                    {"plain_text": "def hello():\n    print('world')"}
                ],
                "language": "python"
            }
        }
        expected = "```python\ndef hello():\n    print('world')\n```"
        self.assertEqual(converter.convert(block), expected)
        
        # Test ohne Sprache
        block = {
            "type": "code",
            "code": {
                "rich_text": [
                    {"plain_text": "console.log('Hello');"}
                ]
            }
        }
        expected = "```\nconsole.log('Hello');\n```"
        self.assertEqual(converter.convert(block), expected)
        
        # Test mit leerem rich_text
        block = {
            "type": "code",
            "code": {
                "rich_text": [],
                "language": "python"
            }
        }
        self.assertIsNone(converter.convert(block))
    
    def test_converter_registration(self):
        """Test für die Registrierung neuer Konverter."""
        # Erstelle einen benutzerdefinierten Konverter
        class CustomConverter(BlockConverter):
            def convert(self, block: Dict[str, Any]):
                return "CUSTOM"
        
        # Registriere den benutzerdefinierten Konverter
        NotionContentConverter.register_converter("custom_type", CustomConverter())
        
        # Prüfe, ob der Konverter korrekt registriert wurde
        block = {"type": "custom_type"}
        blocks = [block]
        result = NotionContentConverter.blocks_to_text(blocks)
        self.assertEqual(result, "CUSTOM")
        
        # Entferne den benutzerdefinierten Konverter nach dem Test
        if "custom_type" in NotionContentConverter._converters:
            del NotionContentConverter._converters["custom_type"]


if __name__ == "__main__":
    unittest.main()