import unittest

from notionary.converters.elements.image_element import ImageElement

class TestImageElement(unittest.TestCase):
    
    def test_match_markdown(self):
        """Test that markdown images are correctly identified."""
        self.assertTrue(ImageElement.match_markdown("![Caption](https://example.com/image.jpg)"))
        self.assertTrue(ImageElement.match_markdown("![](https://example.com/image.jpg)"))
        self.assertTrue(ImageElement.match_markdown("![Caption](https://example.com/image.jpg \"alt text\")"))
        self.assertFalse(ImageElement.match_markdown("[Caption](https://example.com/image.jpg)"))
        self.assertFalse(ImageElement.match_markdown("![Caption]()"))
        self.assertFalse(ImageElement.match_markdown("![Caption](invalid-url)")) 
    
    def test_match_notion(self):
        """Test that Notion image blocks are correctly identified."""
        self.assertTrue(ImageElement.match_notion({"type": "image"}))
        self.assertFalse(ImageElement.match_notion({"type": "paragraph"}))
    
    def test_markdown_to_notion(self):
        """Test conversion from markdown to Notion format."""
        # Test with caption
        image_with_caption = "![Test Caption](https://example.com/image.jpg)"
        expected_with_caption = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": "https://example.com/image.jpg"
                },
                "caption": [
                    {"type": "text", "text": {"content": "Test Caption"}}
                ]
            }
        }
        self.assertEqual(ImageElement.markdown_to_notion(image_with_caption), expected_with_caption)
        
        # Test without caption
        image_without_caption = "![](https://example.com/image.jpg)"
        expected_without_caption = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": "https://example.com/image.jpg"
                }
            }
        }
        self.assertEqual(ImageElement.markdown_to_notion(image_without_caption), expected_without_caption)
        
        # Test invalid markdown
        self.assertIsNone(ImageElement.markdown_to_notion("Not an image"))
    
    def test_notion_to_markdown(self):
        """Test conversion from Notion format to markdown."""
        # Test external image with caption
        notion_external_image = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": "https://example.com/image.jpg"
                },
                "caption": [
                    {"type": "text", "text": {"content": "Test Caption"}}
                ]
            }
        }
        self.assertEqual(
            ImageElement.notion_to_markdown(notion_external_image),
            "![Test Caption](https://example.com/image.jpg)"
        )
        
        # Test file image without caption
        notion_file_image = {
            "type": "image",
            "image": {
                "type": "file",
                "file": {
                    "url": "https://example.com/uploaded.jpg"
                }
            }
        }
        self.assertEqual(
            ImageElement.notion_to_markdown(notion_file_image),
            "![](https://example.com/uploaded.jpg)"
        )
        
        # Test invalid block type
        self.assertIsNone(ImageElement.notion_to_markdown({"type": "paragraph"}))
        
        # Test missing URL
        invalid_image = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {}
            }
        }
        self.assertIsNone(ImageElement.notion_to_markdown(invalid_image))
    
    def test_extract_text_content(self):
        """Test extracting text content from rich_text elements."""
        rich_text = [
            {"type": "text", "text": {"content": "First "}},
            {"type": "text", "text": {"content": "caption"}}
        ]
        self.assertEqual(ImageElement._extract_text_content(rich_text), "First caption")
        
        # Test with plain_text field
        plain_text = [
            {"plain_text": "Another caption"}
        ]
        self.assertEqual(ImageElement._extract_text_content(plain_text), "Another caption")
    
    def test_is_multiline(self):
        """Test that images are not multiline elements."""
        self.assertFalse(ImageElement.is_multiline())

if __name__ == "__main__":
    unittest.main()