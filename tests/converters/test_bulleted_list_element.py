import unittest

from notionary.blocks import BulletedListElement


class TestBulletedListElement(unittest.TestCase):

    def test_match_markdown(self):
        self.assertTrue(BulletedListElement.match_markdown("- Bullet item"))
        self.assertTrue(BulletedListElement.match_markdown("* Another bullet"))
        self.assertTrue(BulletedListElement.match_markdown("+ Yet another bullet"))
        self.assertFalse(BulletedListElement.match_markdown("- [ ] Todo item"))
        self.assertFalse(BulletedListElement.match_markdown("Regular text"))

    def test_match_notion(self):
        self.assertTrue(
            BulletedListElement.match_notion({"type": "bulleted_list_item"})
        )
        self.assertFalse(BulletedListElement.match_notion({"type": "paragraph"}))

    def test_markdown_to_notion(self):
        md = "- A bullet item"
        block = BulletedListElement.markdown_to_notion(md)
        self.assertIsNotNone(block)
        self.assertEqual(block["type"], "bulleted_list_item")
        self.assertEqual(block["bulleted_list_item"]["color"], "default")
        self.assertEqual(
            block["bulleted_list_item"]["rich_text"][0]["text"]["content"],
            "A bullet item",
        )

    def test_notion_to_markdown(self):
        block = {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "List entry"}}],
                "color": "default",
            },
        }
        md = BulletedListElement.notion_to_markdown(block)
        self.assertEqual(md, "- List entry")

    def test_is_multiline(self):
        self.assertFalse(BulletedListElement.is_multiline())
