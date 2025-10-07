from notionary.blocks.markdown.nodes import EquationMarkdownNode


def test_equation_markdown_node():
    """Test EquationMarkdownNode"""
    equation_simple = EquationMarkdownNode(expression="E = mc^2")
    expected = "$$E = mc^2$$"
    assert equation_simple.to_markdown() == expected

    equation_with_parens = EquationMarkdownNode(expression="f(x) = sin(x)")
    expected = "$$f(x) = sin(x)$$"
    assert equation_with_parens.to_markdown() == expected

    equation_with_quotes = EquationMarkdownNode(expression='say "hello"')
    expected = '$$say "hello"$$'
    assert equation_with_quotes.to_markdown() == expected

    equation_empty = EquationMarkdownNode(expression="")
    expected = "$$$$"
    assert equation_empty.to_markdown() == expected

    equation_whitespace = EquationMarkdownNode(expression="   ")
    expected = "$$$$"
    assert equation_whitespace.to_markdown() == expected
