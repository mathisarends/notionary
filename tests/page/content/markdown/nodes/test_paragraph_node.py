from notionary.markdown.nodes import ParagraphMarkdownNode


def test_paragraph_markdown_node() -> None:
    paragraph = ParagraphMarkdownNode(text="This is a paragraph.")
    expected = "This is a paragraph."
    assert paragraph.to_markdown() == expected
