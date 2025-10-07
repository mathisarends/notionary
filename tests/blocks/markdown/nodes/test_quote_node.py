from notionary.blocks.markdown.nodes import QuoteMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_quote_markdown_node() -> None:
    registry = SyntaxRegistry()
    quote_syntax = registry.get_quote_syntax()

    quote = QuoteMarkdownNode(text="This is a quote")
    expected = f"{quote_syntax.start_delimiter} This is a quote"
    assert quote.to_markdown() == expected

    quote_with_author = QuoteMarkdownNode(text="Life is beautiful")
    expected = f"{quote_syntax.start_delimiter} Life is beautiful"
    assert quote_with_author.to_markdown() == expected
