from notionary.page.content.markdown.nodes import CalloutMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_callout_markdown_node_without_emoji(syntax_registry: SyntaxRegistry) -> None:
    callout = CalloutMarkdownNode(text="This is important", syntax_registry=syntax_registry)

    start_delimiter = syntax_registry.get_callout_syntax().start_delimiter
    expected = f"{start_delimiter}(This is important)"

    assert callout.to_markdown() == expected


def test_callout_markdown_node_with_emoji(syntax_registry: SyntaxRegistry) -> None:
    callout = CalloutMarkdownNode(text="Warning!", emoji="⚠️", syntax_registry=syntax_registry)

    start_delimiter = syntax_registry.get_callout_syntax().start_delimiter
    expected = f'{start_delimiter}(Warning! "⚠️")'

    assert callout.to_markdown() == expected


def test_callout_with_single_child(syntax_registry: SyntaxRegistry) -> None:
    child = ParagraphMarkdownNode(text="Important details", syntax_registry=syntax_registry)

    callout = CalloutMarkdownNode(text="Main message", children=[child], syntax_registry=syntax_registry)

    result = callout.to_markdown()
    start_delimiter = syntax_registry.get_callout_syntax().start_delimiter

    assert result.startswith(f"{start_delimiter}(Main message)")

    # Check indented child (4 spaces)
    assert "\n    Important details" in result


def test_callout_with_multiple_children(syntax_registry: SyntaxRegistry) -> None:
    child1 = ParagraphMarkdownNode(text="Important details", syntax_registry=syntax_registry)
    child2 = ParagraphMarkdownNode(text="Additional information", syntax_registry=syntax_registry)

    callout = CalloutMarkdownNode(
        text="Main callout message", emoji="💡", children=[child1, child2], syntax_registry=syntax_registry
    )

    result = callout.to_markdown()
    start_delimiter = syntax_registry.get_callout_syntax().start_delimiter
    expected_parent = f'{start_delimiter}(Main callout message "💡")'

    assert result.startswith(expected_parent)
    # Check both children are indented correctly (4 spaces)
    lines = result.split("\n")
    assert any("    Important details" in line for line in lines), "First child should be indented with 4 spaces"
    assert any("    Additional information" in line for line in lines), "Second child should be indented with 4 spaces"

    # Verify children appear after parent
    parent_index = result.index(expected_parent)
    child1_index = result.index("Important details")
    child2_index = result.index("Additional information")

    assert child1_index > parent_index, "Children should appear after parent"
    assert child2_index > child1_index, "Children should maintain order"


def test_callout_with_empty_children_list(syntax_registry: SyntaxRegistry) -> None:
    callout = CalloutMarkdownNode(text="Test", children=[], syntax_registry=syntax_registry)

    start_delimiter = syntax_registry.get_callout_syntax().start_delimiter
    expected = f"{start_delimiter}(Test)"

    assert callout.to_markdown() == expected
    assert "\n" not in callout.to_markdown(), "Should not have newlines without children"


def test_callout_with_nested_callouts(syntax_registry: SyntaxRegistry) -> None:
    nested_callout = CalloutMarkdownNode(text="Nested warning", emoji="⚠️", syntax_registry=syntax_registry)

    parent_callout = CalloutMarkdownNode(
        text="Parent callout", emoji="📢", children=[nested_callout], syntax_registry=syntax_registry
    )

    result = parent_callout.to_markdown()
    start_delimiter = syntax_registry.get_callout_syntax().start_delimiter

    assert result.startswith(f'{start_delimiter}(Parent callout "📢")')

    expected_nested = f'{start_delimiter}(Nested warning "⚠️")'
    assert f"    {expected_nested}" in result, "Nested callout should be indented"
