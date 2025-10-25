import pytest

from notionary.page.content.markdown.nodes import TableMarkdownNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry
from notionary.page.content.syntax.models import SyntaxDefinition


@pytest.fixture
def table_syntax(syntax_registry: SyntaxDefinitionRegistry) -> SyntaxDefinition:
    return syntax_registry.get_table_syntax()


@pytest.fixture
def table_delimiter(table_syntax: SyntaxDefinition) -> str:
    return table_syntax.start_delimiter


@pytest.fixture
def table_separator(table_syntax: SyntaxDefinition) -> str:
    return table_syntax.end_delimiter


def test_table_markdown_node(table_delimiter: str, table_separator: str) -> None:
    table = TableMarkdownNode(
        headers=["Name", "Age", "City"],
        rows=[["Alice", "25", "Berlin"], ["Bob", "30", "Munich"]],
    )

    d = table_delimiter
    s = table_separator
    expected = (
        f"{d} Name {d} Age {d} City {d}\n"
        f"{d} {s} {d} {s} {d} {s} {d}\n"
        f"{d} Alice {d} 25 {d} Berlin {d}\n"
        f"{d} Bob {d} 30 {d} Munich {d}"
    )

    assert table.to_markdown() == expected
