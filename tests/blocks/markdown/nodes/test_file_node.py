from notionary.blocks.markdown.nodes import FileMarkdownNode
from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.page.content.syntax.service import SyntaxRegistry


def test_file_markdown_node(syntax_registry: SyntaxRegistry, caption_syntax: SyntaxDefinition) -> None:
    file_syntax = syntax_registry.get_file_syntax()

    file = FileMarkdownNode(url="https://example.com/doc.pdf")
    expected = f"{file_syntax.start_delimiter}https://example.com/doc.pdf)"
    assert file.to_markdown() == expected

    file_with_caption = FileMarkdownNode(url="https://example.com/doc.pdf", caption="Important Document")
    expected = f"{file_syntax.start_delimiter}https://example.com/doc.pdf)\n{caption_syntax.start_delimiter} Important Document"
    assert file_with_caption.to_markdown() == expected
