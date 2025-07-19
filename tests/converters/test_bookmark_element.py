import unittest
from notionary.blocks import BookmarkElement


class TestBookmarkElement(unittest.TestCase):
    def test_match_markdown(self):
        """Test die Erkennung von Markdown-Bookmarks."""
        # Gültige Bookmark-Formate
        self.assertTrue(
            BookmarkElement.match_markdown("[bookmark](https://example.com)")
        )
        self.assertTrue(
            BookmarkElement.match_markdown('[bookmark](https://example.com "Titel")')
        )
        self.assertTrue(
            BookmarkElement.match_markdown(
                '[bookmark](https://example.com "Titel" "Beschreibung")'
            )
        )

        # Ungültige Formate
        self.assertFalse(BookmarkElement.match_markdown("[link](https://example.com)"))
        self.assertFalse(BookmarkElement.match_markdown("Dies ist kein Bookmark"))
        self.assertFalse(BookmarkElement.match_markdown("[bookmark](nicht-url)"))

    def test_match_notion(self):
        """Test die Erkennung von Notion-Bookmark-Blöcken."""
        self.assertTrue(
            BookmarkElement.match_notion(
                {"type": "bookmark", "bookmark": {"url": "https://example.com"}}
            )
        )

        self.assertFalse(BookmarkElement.match_notion({"type": "paragraph"}))
        self.assertFalse(
            BookmarkElement.match_notion({"bookmark": {"url": "https://example.com"}})
        )

    def test_markdown_to_notion(self):
        """Test die Konvertierung von Markdown-Bookmarks zu Notion-Bookmark-Blöcken."""
        simple_result = BookmarkElement.markdown_to_notion(
            "[bookmark](https://example.com)"
        )
        self.assertEqual(simple_result["type"], "bookmark")
        self.assertEqual(simple_result["bookmark"]["url"], "https://example.com")
        self.assertNotIn("caption", simple_result["bookmark"])

        titled_result = BookmarkElement.markdown_to_notion(
            '[bookmark](https://example.com "Beispiel-Titel")'
        )
        self.assertEqual(titled_result["type"], "bookmark")
        self.assertEqual(titled_result["bookmark"]["url"], "https://example.com")
        self.assertEqual(
            titled_result["bookmark"]["caption"][0]["text"]["content"], "Beispiel-Titel"
        )

        full_result = BookmarkElement.markdown_to_notion(
            '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")'
        )
        self.assertEqual(full_result["type"], "bookmark")
        self.assertEqual(full_result["bookmark"]["url"], "https://example.com")
        self.assertEqual(
            full_result["bookmark"]["caption"][0]["text"]["content"], "Beispiel-Titel"
        )
        self.assertEqual(
            full_result["bookmark"]["caption"][2]["text"]["content"],
            "Eine Beschreibung",
        )

        # Ungültiges Format
        self.assertIsNone(BookmarkElement.markdown_to_notion("Dies ist kein Bookmark"))

    def test_notion_to_markdown(self):
        """Test die Konvertierung von Notion-Bookmark-Blöcken zu Markdown-Bookmarks."""
        # Einfaches Bookmark
        simple_block = {"type": "bookmark", "bookmark": {"url": "https://example.com"}}
        self.assertEqual(
            BookmarkElement.notion_to_markdown(simple_block),
            "[bookmark](https://example.com)",
        )

        # Bookmark mit Titel
        titled_block = {
            "type": "bookmark",
            "bookmark": {
                "url": "https://example.com",
                "caption": [{"type": "text", "text": {"content": "Beispiel-Titel"}}],
            },
        }
        self.assertEqual(
            BookmarkElement.notion_to_markdown(titled_block),
            '[bookmark](https://example.com "Beispiel-Titel")',
        )

        # Bookmark mit Titel und Beschreibung
        full_block = {
            "type": "bookmark",
            "bookmark": {
                "url": "https://example.com",
                "caption": [
                    {"type": "text", "text": {"content": "Beispiel-Titel"}},
                    {"type": "text", "text": {"content": " - "}},
                    {"type": "text", "text": {"content": "Eine Beschreibung"}},
                ],
            },
        }
        self.assertEqual(
            BookmarkElement.notion_to_markdown(full_block),
            '[bookmark](https://example.com "Beispiel-Titel" "Eine Beschreibung")',
        )

        # Ungültiger Block
        self.assertIsNone(BookmarkElement.notion_to_markdown({"type": "paragraph"}))

    def test_is_multiline(self):
        """Test, dass Bookmarks als einzeilige Elemente erkannt werden."""
        self.assertFalse(BookmarkElement.is_multiline())


if __name__ == "__main__":
    unittest.main()
