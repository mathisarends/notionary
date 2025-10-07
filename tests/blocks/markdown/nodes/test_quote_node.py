from notionary.blocks.markdown.nodes import QuoteMarkdownNode


def test_quote_markdown_node() -> None:
    quote = QuoteMarkdownNode(text="This is a quote")
    expected = "> This is a quote"
    assert quote.to_markdown() == expected

    quote_with_author = QuoteMarkdownNode(text="Life is beautiful")
    expected = "> Life is beautiful"
    assert quote_with_author.to_markdown() == expected
