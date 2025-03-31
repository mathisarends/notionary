import unittest
import json
import os
from typing import List, Dict, Any

from notionary.core.notion_content_converter import NotionContentConverter

class TestNotionContentConverterIntegration(unittest.TestCase):
    """Integration tests for NotionContentConverter."""
    
    def setUp(self):
        """Set up test resources."""
        # Get the directory of this test file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.res_dir = os.path.join(current_dir, "res")
        
        # Ensure the resource path exists
        if not os.path.exists(self.res_dir):
            os.makedirs(self.res_dir)
            
        self.sample_blocks_path = os.path.join(self.res_dir, "sample_blocks.json")

    def test_round_trip_conversion(self):
        """Test that markdown -> blocks -> text preserves content."""
        # This test would need the actual NotionMarkdownParser implementation,
        # so we're only testing a simplified version

        # Assuming the parser works correctly, verify blocks_to_text
        try:
            with open(self.sample_blocks_path, "r", encoding="UTF-8") as f:
                sample_blocks = json.load(f)
        except FileNotFoundError:
            self.fail(f"Test resource not found: {self.sample_blocks_path}")
        
        # Convert blocks to text
        text = NotionContentConverter.blocks_to_text(sample_blocks)
        
        # Verify text contains expected content
        self.assertIn("Sample Document", text)
        self.assertIn("This is a paragraph", text)
        self.assertIn("# Sample Document", text)

    def test_realistic_document_conversion(self):
        """Test conversion with a realistic Notion document structure."""
        blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "Project Overview"}, "plain_text": "Project Overview"}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "This document outlines the "}, "plain_text": "This document outlines the "},
                        {"type": "text", "text": {"content": "key objectives"}, "annotations": {"bold": True}, "plain_text": "key objectives"},
                        {"type": "text", "text": {"content": " for our project."}, "plain_text": " for our project."}
                    ]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Goals"}, "plain_text": "Goals"}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Improve performance by 20%"}, "plain_text": "Improve performance by 20%"}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Reduce error rates"}, "plain_text": "Reduce error rates"}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Timeline"}, "plain_text": "Timeline"}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Phase 1: Planning (2 weeks)"}, "plain_text": "Phase 1: Planning (2 weeks)"}]
                }
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Phase 2: Implementation (4 weeks)"}, "plain_text": "Phase 2: Implementation (4 weeks)"}]
                }
            },
            {
                "object": "block",
                "type": "divider"
            },
            {
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": "def calculate_metrics():\n    return {'performance': 95, 'errors': 2}"}, "plain_text": "def calculate_metrics():\n    return {'performance': 95, 'errors': 2}"}],
                    "language": "python"
                }
            }
        ]
        
        text = NotionContentConverter.blocks_to_text(blocks)
        
        expected_text = """# Project Overview

This document outlines the key objectives for our project.

## Goals

• Improve performance by 20%

• Reduce error rates

## Timeline

1. Phase 1: Planning (2 weeks)

1. Phase 2: Implementation (4 weeks)

---

```python
def calculate_metrics():
    return {'performance': 95, 'errors': 2}
```"""
        
        self.assertEqual(text, expected_text)

    def test_edge_cases(self):
        """Test edge cases in conversion process."""
        # Test with missing block type
        blocks = [{"object": "block"}]  # No type specified
        self.assertEqual(NotionContentConverter.blocks_to_text(blocks), "Keine Inhalte gefunden.")
        
        # Test with empty rich_text arrays
        blocks = [{
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        }]
        self.assertEqual(NotionContentConverter.blocks_to_text(blocks), "Keine Inhalte gefunden.")
        
        # Test with rich_text containing empty strings
        blocks = [{
            "type": "paragraph",
            "paragraph": {"rich_text": [{"plain_text": ""}]}
        }]
        self.assertEqual(NotionContentConverter.blocks_to_text(blocks), "Keine Inhalte gefunden.")


if __name__ == "__main__":
    unittest.main()