from notionary.blocks.markdown.nodes.pdf import PdfMarkdownNode


def test_pdf_markdown_node() -> None:
    pdf = PdfMarkdownNode(url="https://example.com/document.pdf")
    expected = "[pdf](https://example.com/document.pdf)"
    assert pdf.to_markdown() == expected

    pdf_with_caption = PdfMarkdownNode(url="https://example.com/document.pdf", caption="Critical safety information")
    expected = "[pdf](https://example.com/document.pdf)(caption:Critical safety information)"
    assert pdf_with_caption.to_markdown() == expected
