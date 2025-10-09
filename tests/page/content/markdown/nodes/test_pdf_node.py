from notionary.page.content.markdown.nodes.pdf import PdfMarkdownNode
from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.page.content.syntax.service import SyntaxRegistry


def test_pdf_markdown_node(syntax_registry: SyntaxRegistry, caption_syntax: SyntaxDefinition) -> None:
    pdf_syntax = syntax_registry.get_pdf_syntax()

    pdf = PdfMarkdownNode(url="https://example.com/document.pdf")
    expected = f"{pdf_syntax.start_delimiter}https://example.com/document.pdf)"
    assert pdf.to_markdown() == expected

    pdf_with_caption = PdfMarkdownNode(url="https://example.com/document.pdf", caption="Critical safety information")
    expected = f"{pdf_syntax.start_delimiter}https://example.com/document.pdf)\n{caption_syntax.start_delimiter} Critical safety information"
    assert pdf_with_caption.to_markdown() == expected
