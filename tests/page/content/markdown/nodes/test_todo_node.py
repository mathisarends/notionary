from notionary.page.content.markdown.nodes import TodoMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_todo_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    """Test TodoMarkdownNode"""
    todo_syntax = syntax_registry.get_todo_syntax()

    todo = TodoMarkdownNode(text="Buy groceries", checked=False)
    expected = f"- {todo_syntax.start_delimiter} Buy groceries"
    assert todo.to_markdown() == expected

    todo_done = TodoMarkdownNode(text="Finish homework", checked=True)
    expected = f"- {todo_syntax.end_delimiter} Finish homework"
    assert todo_done.to_markdown() == expected

    todo_star = TodoMarkdownNode(text="Important task", checked=False, marker="*")
    expected = f"* {todo_syntax.start_delimiter} Important task"
    assert todo_star.to_markdown() == expected
