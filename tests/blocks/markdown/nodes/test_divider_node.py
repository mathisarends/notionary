from notionary.blocks.markdown.nodes import DividerMarkdownNode


def test_divider_markdown_node() -> None:
    divider = DividerMarkdownNode()
    expected = "---"
    assert divider.to_markdown() == expected
