from notionary.blocks.markdown.nodes import TodoMarkdownNode


def test_todo_markdown_node() -> None:
    """Test TodoMarkdownNode"""
    todo = TodoMarkdownNode(text="Buy groceries", checked=False)
    expected = "- [ ] Buy groceries"
    assert todo.to_markdown() == expected

    todo_done = TodoMarkdownNode(text="Finish homework", checked=True)
    expected = "- [x] Finish homework"
    assert todo_done.to_markdown() == expected

    todo_star = TodoMarkdownNode(text="Important task", checked=False, marker="*")
    expected = "* [ ] Important task"
    assert todo_star.to_markdown() == expected
