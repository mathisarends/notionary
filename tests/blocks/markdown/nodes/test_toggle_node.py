from notionary.blocks.markdown.nodes import (
    ParagraphMarkdownNode,
    ToggleMarkdownNode,
)


def test_toggle_markdown_node() -> None:
    toggle = ToggleMarkdownNode(title="Details", children=[])
    expected = "+++ Details\n+++"
    assert toggle.to_markdown() == expected

    line1_node = ParagraphMarkdownNode(text="Line 1")
    line2_node = ParagraphMarkdownNode(text="Line 2")

    toggle_with_content = ToggleMarkdownNode(
        title="More Info",
        children=[line1_node, line2_node],
    )
    expected = "+++ More Info\nLine 1\n\nLine 2\n+++"
    assert toggle_with_content.to_markdown() == expected
