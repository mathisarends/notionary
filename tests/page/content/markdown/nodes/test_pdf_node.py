import pytest

from notionary.page.content.markdown.nodes.pdf import PdfMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def pdf_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_pdf_syntax().start_delimiter


def test_pdf_without_caption(pdf_delimiter: str) -> None:
    pdf = PdfMarkdownNode(url="https://example.com/document.pdf")
    expected = f"{pdf_delimiter}https://example.com/document.pdf)"

    assert pdf.to_markdown() == expected


def test_pdf_with_caption(pdf_delimiter: str, caption_delimiter: str) -> None:
    pdf = PdfMarkdownNode(
        url="https://example.com/document.pdf", caption="Critical safety information"
    )
    expected = f"{pdf_delimiter}https://example.com/document.pdf)\n{caption_delimiter} Critical safety information"

    assert pdf.to_markdown() == expected
