import unittest
from typing import Dict, Any

from notionary.core.notion_content_converter import (
    NotionContentConverter,
    BlockConverter
)

class TestIntegratedFactoryPattern(unittest.TestCase):
    """Tests für das integrierte Factory Pattern im NotionContentConverter."""
    
    def setUp(self):
        """Test-Ressourcen einrichten."""
        self.complex_document = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "Projektdokumentation"}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "Dies ist eine umfassende Dokumentation für unser Projekt."}
                    ]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"plain_text": "Anforderungen"}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"plain_text": "Funktionale Anforderungen"}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"plain_text": "Nicht-funktionale Anforderungen"}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"plain_text": "Implementierung"}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "Die Implementierung erfolgt in Python mit folgenden Komponenten:"}
                    ]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"plain_text": "Datenmodell"}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"plain_text": "API-Integration"}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"plain_text": "Benutzerschnittstelle"}]
                }
            },
            {
                "object": "block",
                "type": "divider"
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"plain_text": "Code-Beispiel"}]
                }
            },
            {
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"plain_text": "def process_data(data):\n    return {\n        'processed': True,\n        'items': len(data)\n    }"}],
                    "language": "python"
                }
            }
        ]
        
        # Erwartetes Ergebnis für dieses Dokument
        self.expected_output = """# Projektdokumentation

Dies ist eine umfassende Dokumentation für unser Projekt.

## Anforderungen

• Funktionale Anforderungen

• Nicht-funktionale Anforderungen

## Implementierung

Die Implementierung erfolgt in Python mit folgenden Komponenten:

1. Datenmodell

1. API-Integration

1. Benutzerschnittstelle

---

### Code-Beispiel

```python
def process_data(data):
    return {
        'processed': True,
        'items': len(data)
    }
```"""
    
    def test_complex_document_conversion(self):
        """Test der Konvertierung eines komplexen Dokuments."""
        result = NotionContentConverter.blocks_to_text(self.complex_document)
        self.assertEqual(result, self.expected_output)
    
    def test_mixed_known_and_unknown_blocks(self):
        """Test der Konvertierung mit bekannten und unbekannten Block-Typen."""
        mixed_blocks = self.complex_document.copy()
        mixed_blocks.insert(2, {
            "object": "block",
            "type": "unknown_type",
            "unknown_type": {
                "rich_text": [{"plain_text": "Dies sollte ignoriert werden"}]
            }
        })
        
        # Das Ergebnis sollte dasselbe sein wie bei self.expected_output,
        # da der unbekannte Block-Typ ignoriert werden sollte
        result = NotionContentConverter.blocks_to_text(mixed_blocks)
        self.assertEqual(result, self.expected_output)
    
    def test_custom_converter_integration(self):
        """Test der Integration eines benutzerdefinierten Konverters."""
        # Erstelle einen benutzerdefinierten Konverter für einen neuen Block-Typ
        class QuoteConverter(BlockConverter):
            def convert(self, block: Dict[str, Any]):
                quote_data = block.get("quote", {})
                rich_text = quote_data.get("rich_text", [])
                text = NotionContentConverter.extract_text_from_rich_text(rich_text)
                return f"> {text}" if text else None
        
        # Registriere den benutzerdefinierten Konverter
        NotionContentConverter.register_converter("quote", QuoteConverter())
        
        # Erstelle ein Dokument mit dem neuen Block-Typ
        blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"plain_text": "Zitate"}]
                }
            },
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [{"plain_text": "Dies ist ein wichtiges Zitat."}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "Und hier ein Kommentar dazu."}]
                }
            }
        ]
        
        expected = "# Zitate\n\n> Dies ist ein wichtiges Zitat.\n\nUnd hier ein Kommentar dazu."
        result = NotionContentConverter.blocks_to_text(blocks)
        self.assertEqual(result, expected)
        
        # Entferne den benutzerdefinierten Konverter nach dem Test
        if "quote" in NotionContentConverter.get_converters():
            del NotionContentConverter.get_converters()["quote"]
    
    def test_sequential_conversions(self):
        """Test mehrerer aufeinanderfolgender Konvertierungen."""
        # Führe mehrere Konvertierungen hintereinander aus, um sicherzustellen,
        # dass der Zustand des Konverters konsistent bleibt
        for _ in range(3):
            result = NotionContentConverter.blocks_to_text(self.complex_document)
            self.assertEqual(result, self.expected_output)


if __name__ == "__main__":
    unittest.main()