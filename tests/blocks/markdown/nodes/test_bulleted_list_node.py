from notionary.blocks.markdown.nodes import BulletedListMarkdownNode


def test_bulleted_list_markdown_node() -> None:
    bulleted_list = BulletedListMarkdownNode(texts=["Item 1", "Item 2", "Item 3"])
    expected = "- Item 1\n- Item 2\n- Item 3"
    assert bulleted_list.to_markdown() == expected
