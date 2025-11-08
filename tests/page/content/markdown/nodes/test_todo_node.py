import pytest

from notionary.markdown.nodes import (
    ParagraphMarkdownNode,
    TodoMarkdownNode,
)
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry


@pytest.fixture
def todo_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_todo_syntax().start_delimiter


@pytest.fixture
def todo_marker() -> str:
    return "-"


def test_unchecked_todo(
    syntax_registry: SyntaxDefinitionRegistry, todo_delimiter: str, todo_marker: str
) -> None:
    todo = TodoMarkdownNode(
        text="Buy groceries", checked=False, syntax_registry=syntax_registry
    )
    expected = f"{todo_delimiter} Buy groceries"

    assert todo.to_markdown() == expected


def test_checked_todo(
    syntax_registry: SyntaxDefinitionRegistry, todo_marker: str
) -> None:
    todo = TodoMarkdownNode(
        text="Finish homework", checked=True, syntax_registry=syntax_registry
    )
    todo_done_syntax = syntax_registry.get_todo_done_syntax()
    expected = f"{todo_done_syntax.start_delimiter} Finish homework"

    assert todo.to_markdown() == expected


def test_todo_with_explicit_dash_marker(
    syntax_registry: SyntaxDefinitionRegistry, todo_delimiter: str, todo_marker: str
) -> None:
    todo = TodoMarkdownNode(
        text="Important task",
        checked=False,
        marker="-",
        syntax_registry=syntax_registry,
    )
    expected = f"{todo_delimiter} Important task"

    assert todo.to_markdown() == expected


def test_todo_with_invalid_marker_falls_back_to_dash(
    syntax_registry: SyntaxDefinitionRegistry, todo_delimiter: str, todo_marker: str
) -> None:
    todo = TodoMarkdownNode(
        text="Task with star marker",
        checked=False,
        marker="*",
        syntax_registry=syntax_registry,
    )
    expected = f"{todo_delimiter} Task with star marker"

    assert todo.to_markdown() == expected


def test_todo_with_another_invalid_marker_falls_back_to_dash(
    syntax_registry: SyntaxDefinitionRegistry, todo_delimiter: str, todo_marker: str
) -> None:
    todo = TodoMarkdownNode(
        text="Task with plus marker",
        checked=False,
        marker="+",
        syntax_registry=syntax_registry,
    )
    expected = f"{todo_delimiter} Task with plus marker"

    assert todo.to_markdown() == expected


def test_todo_with_paragraph_child(
    syntax_registry: SyntaxDefinitionRegistry,
    todo_delimiter: str,
    todo_marker: str,
    indent: str,
) -> None:
    child = ParagraphMarkdownNode(
        text="Additional notes", syntax_registry=syntax_registry
    )
    todo = TodoMarkdownNode(
        text="Main task",
        checked=False,
        children=[child],
        syntax_registry=syntax_registry,
    )

    result = todo.to_markdown()

    assert f"{todo_delimiter} Main task" in result
    assert f"{indent}Additional notes" in result


def test_todo_with_nested_todo_child(
    syntax_registry: SyntaxDefinitionRegistry,
    todo_delimiter: str,
    todo_marker: str,
    indent: str,
) -> None:
    nested_todo = TodoMarkdownNode(
        text="Sub-task", checked=False, syntax_registry=syntax_registry
    )
    parent_todo = TodoMarkdownNode(
        text="Main task",
        checked=False,
        children=[nested_todo],
        syntax_registry=syntax_registry,
    )

    result = parent_todo.to_markdown()

    assert f"{todo_delimiter} Main task" in result
    assert f"{indent}{todo_delimiter} Sub-task" in result


def test_todo_with_multiple_children(
    syntax_registry: SyntaxDefinitionRegistry,
    todo_delimiter: str,
    todo_marker: str,
    indent: str,
) -> None:
    first_child = ParagraphMarkdownNode(
        text="Additional notes", syntax_registry=syntax_registry
    )
    second_child = TodoMarkdownNode(
        text="Sub-task", checked=False, syntax_registry=syntax_registry
    )
    todo = TodoMarkdownNode(
        text="Main task",
        checked=False,
        children=[first_child, second_child],
        syntax_registry=syntax_registry,
    )

    result = todo.to_markdown()

    assert f"{todo_delimiter} Main task" in result
    assert f"{indent}Additional notes" in result
    assert f"{indent}{todo_delimiter} Sub-task" in result


def test_checked_todo_with_children(
    syntax_registry: SyntaxDefinitionRegistry, todo_marker: str, indent: str
) -> None:
    child = ParagraphMarkdownNode(
        text="Completion notes", syntax_registry=syntax_registry
    )
    todo = TodoMarkdownNode(
        text="Completed task",
        checked=True,
        children=[child],
        syntax_registry=syntax_registry,
    )

    result = todo.to_markdown()
    todo_done_syntax = syntax_registry.get_todo_done_syntax()

    assert f"{todo_done_syntax.start_delimiter} Completed task" in result
    assert f"{indent}Completion notes" in result


def test_todo_without_children(
    syntax_registry: SyntaxDefinitionRegistry, todo_delimiter: str, todo_marker: str
) -> None:
    todo = TodoMarkdownNode(
        text="Simple task", checked=False, children=[], syntax_registry=syntax_registry
    )
    expected = f"{todo_delimiter} Simple task"

    result = todo.to_markdown()

    assert result == expected
    assert "\n" not in result


def test_todo_children_order_preserved(
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    first_child = ParagraphMarkdownNode(text="First", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second", syntax_registry=syntax_registry)
    todo = TodoMarkdownNode(
        text="Main task",
        checked=False,
        children=[first_child, second_child],
        syntax_registry=syntax_registry,
    )

    result = todo.to_markdown()
    first_position = result.index("First")
    second_position = result.index("Second")

    assert first_position < second_position


def test_todo_with_empty_text(
    syntax_registry: SyntaxDefinitionRegistry, todo_delimiter: str, todo_marker: str
) -> None:
    todo = TodoMarkdownNode(text="", checked=False, syntax_registry=syntax_registry)
    expected = f"{todo_delimiter} "

    assert todo.to_markdown() == expected
