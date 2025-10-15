from notionary.page.content.markdown.nodes import ParagraphMarkdownNode, QuoteMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_simple_quote(syntax_registry: SyntaxRegistry) -> None:
    quote = QuoteMarkdownNode(text="This is a quote", syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_quote_syntax().start_delimiter
    expected = f"{delimiter} This is a quote"

    assert quote.to_markdown() == expected


def test_quote_with_different_text(syntax_registry: SyntaxRegistry) -> None:
    quote = QuoteMarkdownNode(text="Life is beautiful", syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_quote_syntax().start_delimiter
    expected = f"{delimiter} Life is beautiful"

    assert quote.to_markdown() == expected


def test_quote_with_single_paragraph_child(syntax_registry: SyntaxRegistry) -> None:
    child = ParagraphMarkdownNode(text="Attribution text", syntax_registry=syntax_registry)

    quote = QuoteMarkdownNode(text="Main quote text", children=[child], syntax_registry=syntax_registry)

    result = quote.to_markdown()
    delimiter = syntax_registry.get_quote_syntax().start_delimiter

    assert result.startswith(f"{delimiter} Main quote text")
    assert "\n    Attribution text" in result


def test_quote_with_multiple_children(syntax_registry: SyntaxRegistry) -> None:
    first_child = ParagraphMarkdownNode(text="Attribution text", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Additional context", syntax_registry=syntax_registry)

    quote = QuoteMarkdownNode(
        text="Main quote text", children=[first_child, second_child], syntax_registry=syntax_registry
    )

    result = quote.to_markdown()
    delimiter = syntax_registry.get_quote_syntax().start_delimiter

    assert result.startswith(f"{delimiter} Main quote text")
    assert "    Attribution text" in result
    assert "    Additional context" in result


def test_quote_without_children(syntax_registry: SyntaxRegistry) -> None:
    quote = QuoteMarkdownNode(text="Standalone quote", children=[], syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_quote_syntax().start_delimiter
    expected = f"{delimiter} Standalone quote"

    assert quote.to_markdown() == expected
    assert "\n" not in quote.to_markdown()


def test_quote_with_nested_quote_child(syntax_registry: SyntaxRegistry) -> None:
    nested_quote = QuoteMarkdownNode(text="Nested quote", syntax_registry=syntax_registry)

    parent_quote = QuoteMarkdownNode(text="Parent quote", children=[nested_quote], syntax_registry=syntax_registry)

    result = parent_quote.to_markdown()
    delimiter = syntax_registry.get_quote_syntax().start_delimiter

    assert result.startswith(f"{delimiter} Parent quote")
    assert f"    {delimiter} Nested quote" in result


def test_quote_children_order_preserved(syntax_registry: SyntaxRegistry) -> None:
    first_child = ParagraphMarkdownNode(text="First", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second", syntax_registry=syntax_registry)
    third_child = ParagraphMarkdownNode(text="Third", syntax_registry=syntax_registry)

    quote = QuoteMarkdownNode(
        text="Main quote", children=[first_child, second_child, third_child], syntax_registry=syntax_registry
    )

    result = quote.to_markdown()
    first_position = result.index("First")
    second_position = result.index("Second")
    third_position = result.index("Third")

    assert first_position < second_position < third_position


def test_quote_with_empty_text(syntax_registry: SyntaxRegistry) -> None:
    quote = QuoteMarkdownNode(text="", syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_quote_syntax().start_delimiter
    expected = f"{delimiter} "

    assert quote.to_markdown() == expected
