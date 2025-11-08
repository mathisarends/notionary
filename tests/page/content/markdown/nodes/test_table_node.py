import pytest

from notionary.markdown.nodes import TableMarkdownNode
from notionary.markdown.syntax.definition.models import SyntaxDefinition
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry


@pytest.fixture
def table_syntax(syntax_registry: SyntaxDefinitionRegistry) -> SyntaxDefinition:
    return syntax_registry.get_table_syntax()


@pytest.fixture
def table_delimiter(table_syntax: SyntaxDefinition) -> str:
    return table_syntax.start_delimiter


@pytest.fixture
def table_separator(table_syntax: SyntaxDefinition) -> str:
    # Separator for table rows is a dash character, not an end_delimiter
    return "-"


def test_table_markdown_node(table_delimiter: str, table_separator: str) -> None:
    table = TableMarkdownNode(
        headers=["Name", "Age", "City"],
        rows=[["Alice", "25", "Berlin"], ["Bob", "30", "Munich"]],
    )

    delimiter = table_delimiter
    separator = table_separator
    expected = (
        f"{delimiter} Name {delimiter} Age {delimiter} City {delimiter}\n"
        f"{delimiter} {separator} {delimiter} {separator} {delimiter} {separator} {delimiter}\n"
        f"{delimiter} Alice {delimiter} 25 {delimiter} Berlin {delimiter}\n"
        f"{delimiter} Bob {delimiter} 30 {delimiter} Munich {delimiter}"
    )

    assert table.to_markdown() == expected
