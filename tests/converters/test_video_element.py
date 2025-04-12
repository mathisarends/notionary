import unittest

from notionary.core.converters.elements.video_element import VideoElement

class TestVideoElement(unittest.TestCase):

    def test_match_markdown(self):
        """Test that markdown video embeds are correctly identified."""
        self.assertTrue(
            VideoElement.match_markdown("@[Caption](https://example.com/video.mp4)")
        )
        self.assertTrue(
            VideoElement.match_markdown("@[](https://example.com/video.mp4)")
        )
        self.assertTrue(
            VideoElement.match_markdown(
                "@[Caption](https://youtube.com/watch?v=abc123)"
            )
        )
        self.assertFalse(
            VideoElement.match_markdown("![Caption](https://example.com/video.mp4)")
        )
        self.assertFalse(VideoElement.match_markdown("@[Caption](not-a-url)"))
        self.assertFalse(VideoElement.match_markdown("@[Caption]()"))

    def test_match_notion(self):
        """Test that Notion video blocks are correctly identified."""
        self.assertTrue(VideoElement.match_notion({"type": "video"}))
        self.assertFalse(VideoElement.match_notion({"type": "image"}))

    def test_markdown_to_notion(self):
        """Test conversion from markdown to Notion video block."""
        md = "@[My Caption](https://example.com/video.mp4)"
        expected = {
            "type": "video",
            "video": {
                "type": "external",
                "external": {"url": "https://example.com/video.mp4"},
                "caption": [{"type": "text", "text": {"content": "My Caption"}}],
            },
        }
        self.assertEqual(VideoElement.markdown_to_notion(md), expected)

        # Without caption
        md_no_caption = "@[](https://example.com/video.mp4)"
        expected_no_caption = {
            "type": "video",
            "video": {
                "type": "external",
                "external": {"url": "https://example.com/video.mp4"},
            },
        }
        self.assertEqual(
            VideoElement.markdown_to_notion(md_no_caption), expected_no_caption
        )

        self.assertIsNone(VideoElement.markdown_to_notion("Not a video"))

    def test_notion_to_markdown(self):
        """Test conversion from Notion video block to markdown."""
        block = {
            "type": "video",
            "video": {
                "type": "external",
                "external": {"url": "https://example.com/video.mp4"},
                "caption": [{"type": "text", "text": {"content": "My Caption"}}],
            },
        }
        self.assertEqual(
            VideoElement.notion_to_markdown(block),
            "@[My Caption](https://example.com/video.mp4)",
        )

        # File without caption
        block_file = {
            "type": "video",
            "video": {
                "type": "file",
                "file": {"url": "https://example.com/uploaded.mp4"},
            },
        }
        self.assertEqual(
            VideoElement.notion_to_markdown(block_file),
            "@[](https://example.com/uploaded.mp4)",
        )

        # Invalid type
        self.assertIsNone(VideoElement.notion_to_markdown({"type": "paragraph"}))

        # Missing URL
        block_missing_url = {
            "type": "video",
            "video": {"type": "external", "external": {}},
        }
        self.assertIsNone(VideoElement.notion_to_markdown(block_missing_url))

    def test_extract_text_content(self):
        """Test caption extraction from rich_text."""
        rt = [
            {"type": "text", "text": {"content": "This "}},
            {"type": "text", "text": {"content": "works"}},
        ]
        self.assertEqual(VideoElement._extract_text_content(rt), "This works")

        # Plain text fallback
        pt = [{"plain_text": "Backup"}]
        self.assertEqual(VideoElement._extract_text_content(pt), "Backup")

    def test_is_multiline(self):
        """Test that videos are not multiline."""
        self.assertFalse(VideoElement.is_multiline())


if __name__ == "__main__":
    unittest.main()
