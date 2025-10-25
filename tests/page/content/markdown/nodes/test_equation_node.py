import pytest

from notionary.page.content.markdown.nodes import EquationMarkdownNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry
from notionary.page.content.syntax.models import SyntaxDefinition


@pytest.fixture
def equation_syntax(syntax_registry: SyntaxDefinitionRegistry) -> SyntaxDefinition:
    return syntax_registry.get_equation_syntax()


@pytest.fixture
def equation_start_delimiter(equation_syntax: SyntaxDefinition) -> str:
    return equation_syntax.start_delimiter


@pytest.fixture
def equation_end_delimiter(equation_syntax: SyntaxDefinition) -> str:
    return equation_syntax.end_delimiter


def test_equation_simple(equation_start_delimiter: str, equation_end_delimiter: str) -> None:
    equation = EquationMarkdownNode(expression="E = mc^2")
    expected = f"{equation_start_delimiter}E = mc^2{equation_end_delimiter}"

    assert equation.to_markdown() == expected


def test_equation_with_parens(equation_start_delimiter: str, equation_end_delimiter: str) -> None:
    equation = EquationMarkdownNode(expression="f(x) = sin(x)")
    expected = f"{equation_start_delimiter}f(x) = sin(x){equation_end_delimiter}"

    assert equation.to_markdown() == expected


def test_equation_with_quotes(equation_start_delimiter: str, equation_end_delimiter: str) -> None:
    equation = EquationMarkdownNode(expression='say "hello"')
    expected = f'{equation_start_delimiter}say "hello"{equation_end_delimiter}'

    assert equation.to_markdown() == expected


def test_equation_empty(equation_start_delimiter: str, equation_end_delimiter: str) -> None:
    equation = EquationMarkdownNode(expression="")
    expected = f"{equation_start_delimiter}{equation_end_delimiter}"

    assert equation.to_markdown() == expected


def test_equation_whitespace(equation_start_delimiter: str, equation_end_delimiter: str) -> None:
    equation = EquationMarkdownNode(expression="   ")
    expected = f"{equation_start_delimiter}{equation_end_delimiter}"

    assert equation.to_markdown() == expected
