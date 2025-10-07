from notionary.blocks.markdown.nodes import FileMarkdownNode


def test_file_markdown_node() -> None:
    file = FileMarkdownNode(url="https://example.com/doc.pdf")
    expected = "[file](https://example.com/doc.pdf)"
    assert file.to_markdown() == expected

    file_with_caption = FileMarkdownNode(url="https://example.com/doc.pdf", caption="Important Document")
    expected = "[file](https://example.com/doc.pdf)(caption:Important Document)"
    assert file_with_caption.to_markdown() == expected
