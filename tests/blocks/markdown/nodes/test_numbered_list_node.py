from notionary.blocks.markdown.nodes import NumberedListMarkdownNode


def test_numbered_list_markdown_node() -> None:
    numbered_list = NumberedListMarkdownNode(texts=["First", "Second", "Third"])
    expected = "1. First\n2. Second\n3. Third"
    assert numbered_list.to_markdown() == expected
