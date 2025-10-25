import pytest

from notionary.page.content.markdown.nodes import ParagraphMarkdownNode, ToggleMarkdownNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry


@pytest.fixture
def toggle_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_toggle_syntax().start_delimiter


def test_simple_toggle(syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str) -> None:
    toggle = ToggleMarkdownNode(title="Details", syntax_registry=syntax_registry)
    expected = f"{toggle_delimiter} Details"

    assert toggle.to_markdown() == expected


def test_toggle_without_children(syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str) -> None:
    toggle = ToggleMarkdownNode(title="No content", children=[], syntax_registry=syntax_registry)
    expected = f"{toggle_delimiter} No content"

    result = toggle.to_markdown()

    assert result == expected
    assert "\n" not in result


def test_toggle_with_single_paragraph_child(
    syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str, indent: str
) -> None:
    child = ParagraphMarkdownNode(text="Hidden content", syntax_registry=syntax_registry)
    toggle = ToggleMarkdownNode(title="Click to expand", children=[child], syntax_registry=syntax_registry)

    result = toggle.to_markdown()

    assert result.startswith(f"{toggle_delimiter} Click to expand")
    assert f"{indent}Hidden content" in result


def test_toggle_with_multiple_children(
    syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str, indent: str
) -> None:
    first_child = ParagraphMarkdownNode(text="Line 1", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Line 2", syntax_registry=syntax_registry)
    toggle = ToggleMarkdownNode(
        title="More Info", children=[first_child, second_child], syntax_registry=syntax_registry
    )

    result = toggle.to_markdown()

    assert result.startswith(f"{toggle_delimiter} More Info")
    assert f"{indent}Line 1" in result
    assert f"{indent}Line 2" in result


def test_toggle_with_nested_toggle_child(
    syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str, indent: str
) -> None:
    nested_toggle = ToggleMarkdownNode(title="Nested section", syntax_registry=syntax_registry)
    parent_toggle = ToggleMarkdownNode(title="Main section", children=[nested_toggle], syntax_registry=syntax_registry)

    result = parent_toggle.to_markdown()

    assert result.startswith(f"{toggle_delimiter} Main section")
    assert f"{indent}{toggle_delimiter} Nested section" in result


def test_toggle_with_mixed_children(
    syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str, indent: str
) -> None:
    paragraph = ParagraphMarkdownNode(text="Some text", syntax_registry=syntax_registry)
    nested_toggle = ToggleMarkdownNode(title="Nested", syntax_registry=syntax_registry)
    toggle = ToggleMarkdownNode(
        title="Mixed content", children=[paragraph, nested_toggle], syntax_registry=syntax_registry
    )

    result = toggle.to_markdown()

    assert f"{toggle_delimiter} Mixed content" in result
    assert f"{indent}Some text" in result
    assert f"{indent}{toggle_delimiter} Nested" in result


def test_toggle_children_order_preserved(syntax_registry: SyntaxDefinitionRegistry) -> None:
    first_child = ParagraphMarkdownNode(text="First", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second", syntax_registry=syntax_registry)
    third_child = ParagraphMarkdownNode(text="Third", syntax_registry=syntax_registry)
    toggle = ToggleMarkdownNode(
        title="Ordered content", children=[first_child, second_child, third_child], syntax_registry=syntax_registry
    )

    result = toggle.to_markdown()
    first_position = result.index("First")
    second_position = result.index("Second")
    third_position = result.index("Third")

    assert first_position < second_position < third_position


def test_toggle_with_empty_title(syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str) -> None:
    toggle = ToggleMarkdownNode(title="", syntax_registry=syntax_registry)
    expected = f"{toggle_delimiter} "

    assert toggle.to_markdown() == expected


def test_toggle_with_long_title(syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str) -> None:
    long_title = "This is a very long toggle title that contains a lot of information"
    toggle = ToggleMarkdownNode(title=long_title, syntax_registry=syntax_registry)
    expected = f"{toggle_delimiter} {long_title}"

    assert toggle.to_markdown() == expected


def test_deeply_nested_toggles(syntax_registry: SyntaxDefinitionRegistry, toggle_delimiter: str, indent: str) -> None:
    innermost = ToggleMarkdownNode(title="Level 3", syntax_registry=syntax_registry)
    middle = ToggleMarkdownNode(title="Level 2", children=[innermost], syntax_registry=syntax_registry)
    outer = ToggleMarkdownNode(title="Level 1", children=[middle], syntax_registry=syntax_registry)

    result = outer.to_markdown()

    assert f"{toggle_delimiter} Level 1" in result
    assert f"{indent}{toggle_delimiter} Level 2" in result
    assert f"{indent}{indent}{toggle_delimiter} Level 3" in result
