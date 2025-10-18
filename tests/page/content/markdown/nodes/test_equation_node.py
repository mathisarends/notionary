from notionary.page.content.markdown.nodes import EquationMarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


def test_equation_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    """Test EquationMarkdownNode"""
    equation_syntax = syntax_registry.get_equation_syntax()

    equation_simple = EquationMarkdownNode(expression="E = mc^2")
    expected = f"{equation_syntax.start_delimiter}E = mc^2{equation_syntax.end_delimiter}"
    assert equation_simple.to_markdown() == expected

    equation_with_parens = EquationMarkdownNode(expression="f(x) = sin(x)")
    expected = f"{equation_syntax.start_delimiter}f(x) = sin(x){equation_syntax.end_delimiter}"
    assert equation_with_parens.to_markdown() == expected

    equation_with_quotes = EquationMarkdownNode(expression='say "hello"')
    expected = f'{equation_syntax.start_delimiter}say "hello"{equation_syntax.end_delimiter}'
    assert equation_with_quotes.to_markdown() == expected

    equation_empty = EquationMarkdownNode(expression="")
    expected = f"{equation_syntax.start_delimiter}{equation_syntax.end_delimiter}"
    assert equation_empty.to_markdown() == expected

    equation_whitespace = EquationMarkdownNode(expression="   ")
    expected = f"{equation_syntax.start_delimiter}{equation_syntax.end_delimiter}"
    assert equation_whitespace.to_markdown() == expected
