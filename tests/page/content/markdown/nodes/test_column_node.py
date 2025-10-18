import pytest

from notionary.page.content.markdown.nodes import ColumnMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.markdown.nodes.columns import ColumnListMarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


@pytest.fixture
def column_delimiter(syntax_registry: SyntaxRegistry) -> str:
    return syntax_registry.get_column_syntax().start_delimiter


@pytest.fixture
def column_list_delimiter(syntax_registry: SyntaxRegistry) -> str:
    return syntax_registry.get_column_list_syntax().start_delimiter


def test_column_without_width_ratio(syntax_registry: SyntaxRegistry, column_delimiter: str) -> None:
    column = ColumnMarkdownNode(syntax_registry=syntax_registry)
    expected = column_delimiter

    assert column.to_markdown() == expected


def test_column_with_width_ratio(syntax_registry: SyntaxRegistry, column_delimiter: str) -> None:
    column = ColumnMarkdownNode(width_ratio=0.5, syntax_registry=syntax_registry)
    expected = f"{column_delimiter} 0.5"

    assert column.to_markdown() == expected


def test_column_with_children(syntax_registry: SyntaxRegistry, column_delimiter: str, indent: str) -> None:
    child = ParagraphMarkdownNode(text="Column content", syntax_registry=syntax_registry)
    column = ColumnMarkdownNode(children=[child], syntax_registry=syntax_registry)

    result = column.to_markdown()

    assert result.startswith(column_delimiter)
    assert f"{indent}Column content" in result


def test_column_list_without_columns(syntax_registry: SyntaxRegistry, column_list_delimiter: str) -> None:
    column_list = ColumnListMarkdownNode(syntax_registry=syntax_registry)
    expected = column_list_delimiter

    assert column_list.to_markdown() == expected


def test_column_list_with_columns(
    syntax_registry: SyntaxRegistry, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    column1 = ColumnMarkdownNode(width_ratio=0.5, syntax_registry=syntax_registry)
    column2 = ColumnMarkdownNode(width_ratio=0.5, syntax_registry=syntax_registry)
    column_list = ColumnListMarkdownNode(columns=[column1, column2], syntax_registry=syntax_registry)

    result = column_list.to_markdown()

    assert result.startswith(column_list_delimiter)
    assert f"{indent}{column_delimiter} 0.5" in result
