from notionary.page.content.markdown.nodes import ColumnMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.markdown.nodes.columns import ColumnListMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_column_without_width_ratio(syntax_registry: SyntaxRegistry) -> None:
    column = ColumnMarkdownNode(syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    expected = delimiter

    assert column.to_markdown() == expected


def test_column_with_width_ratio(syntax_registry: SyntaxRegistry) -> None:
    column = ColumnMarkdownNode(width_ratio=0.5, syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    expected = f"{delimiter} 0.5"

    assert column.to_markdown() == expected


def test_column_with_children(syntax_registry: SyntaxRegistry) -> None:
    child = ParagraphMarkdownNode(text="Column content", syntax_registry=syntax_registry)

    column = ColumnMarkdownNode(children=[child], syntax_registry=syntax_registry)

    result = column.to_markdown()
    delimiter = syntax_registry.get_column_syntax().start_delimiter

    assert result.startswith(delimiter)
    assert "    Column content" in result


def test_column_list_without_columns(syntax_registry: SyntaxRegistry) -> None:
    column_list = ColumnListMarkdownNode(syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    expected = delimiter

    assert column_list.to_markdown() == expected


def test_column_list_with_columns(syntax_registry: SyntaxRegistry) -> None:
    column1 = ColumnMarkdownNode(width_ratio=0.5, syntax_registry=syntax_registry)
    column2 = ColumnMarkdownNode(width_ratio=0.5, syntax_registry=syntax_registry)

    column_list = ColumnListMarkdownNode(columns=[column1, column2], syntax_registry=syntax_registry)

    result = column_list.to_markdown()
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    column_delimiter = syntax_registry.get_column_syntax().start_delimiter

    assert result.startswith(delimiter)
    assert f"    {column_delimiter} 0.5" in result
