import pytest

from notionary.page.content.markdown.nodes import CalloutMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


@pytest.fixture
def callout_delimiter(syntax_registry: SyntaxRegistry) -> str:
    return syntax_registry.get_callout_syntax().start_delimiter


def test_callout_without_emoji(syntax_registry: SyntaxRegistry, callout_delimiter: str) -> None:
    callout = CalloutMarkdownNode(text="This is important", syntax_registry=syntax_registry)
    expected = f"{callout_delimiter}(This is important)"

    assert callout.to_markdown() == expected


def test_callout_with_emoji(syntax_registry: SyntaxRegistry, callout_delimiter: str) -> None:
    callout = CalloutMarkdownNode(text="Warning!", emoji="⚠️", syntax_registry=syntax_registry)
    expected = f'{callout_delimiter}(Warning! "⚠️")'

    assert callout.to_markdown() == expected


def test_callout_with_single_child(syntax_registry: SyntaxRegistry, callout_delimiter: str, indent: str) -> None:
    child = ParagraphMarkdownNode(text="Important details", syntax_registry=syntax_registry)
    callout = CalloutMarkdownNode(text="Main message", children=[child], syntax_registry=syntax_registry)

    result = callout.to_markdown()

    assert result.startswith(f"{callout_delimiter}(Main message)")
    assert f"\n{indent}Important details" in result


def test_callout_with_multiple_children(syntax_registry: SyntaxRegistry, callout_delimiter: str, indent: str) -> None:
    child1 = ParagraphMarkdownNode(text="Important details", syntax_registry=syntax_registry)
    child2 = ParagraphMarkdownNode(text="Additional information", syntax_registry=syntax_registry)
    callout = CalloutMarkdownNode(
        text="Main callout message", emoji="💡", children=[child1, child2], syntax_registry=syntax_registry
    )

    result = callout.to_markdown()
    expected_parent = f'{callout_delimiter}(Main callout message "💡")'
    lines = result.split("\n")

    assert result.startswith(expected_parent)
    assert any(f"{indent}Important details" in line for line in lines)
    assert any(f"{indent}Additional information" in line for line in lines)

    parent_index = result.index(expected_parent)
    child1_index = result.index("Important details")
    child2_index = result.index("Additional information")

    assert child1_index > parent_index
    assert child2_index > child1_index


def test_callout_with_empty_children_list(syntax_registry: SyntaxRegistry, callout_delimiter: str) -> None:
    callout = CalloutMarkdownNode(text="Test", children=[], syntax_registry=syntax_registry)
    expected = f"{callout_delimiter}(Test)"

    result = callout.to_markdown()

    assert result == expected
    assert "\n" not in result


def test_callout_with_nested_callouts(syntax_registry: SyntaxRegistry, callout_delimiter: str, indent: str) -> None:
    nested_callout = CalloutMarkdownNode(text="Nested warning", emoji="⚠️", syntax_registry=syntax_registry)
    parent_callout = CalloutMarkdownNode(
        text="Parent callout", emoji="📢", children=[nested_callout], syntax_registry=syntax_registry
    )

    result = parent_callout.to_markdown()
    expected_nested = f'{callout_delimiter}(Nested warning "⚠️")'

    assert result.startswith(f'{callout_delimiter}(Parent callout "📢")')
    assert f"{indent}{expected_nested}" in result
