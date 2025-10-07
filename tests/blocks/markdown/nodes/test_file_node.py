from notionary.blocks.markdown.nodes import FileMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_file_markdown_node() -> None:
    registry = SyntaxRegistry()
    file_syntax = registry.get_file_syntax()
    caption_syntax = registry.get_caption_syntax()

    file = FileMarkdownNode(url="https://example.com/doc.pdf")
    expected = f"{file_syntax.start_delimiter}https://example.com/doc.pdf)"
    assert file.to_markdown() == expected

    file_with_caption = FileMarkdownNode(url="https://example.com/doc.pdf", caption="Important Document")
    expected = f"{file_syntax.start_delimiter}https://example.com/doc.pdf)\n{caption_syntax.start_delimiter} Important Document"
    assert file_with_caption.to_markdown() == expected
