import pytest

from notionary.page.content.markdown.nodes import BulletedListMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def bulleted_list_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_bulleted_list_syntax().start_delimiter


def test_simple_bulleted_list(syntax_registry: SyntaxDefinitionRegistry, bulleted_list_delimiter: str) -> None:
    bulleted_list = BulletedListMarkdownNode(texts=["Item 1", "Item 2", "Item 3"], syntax_registry=syntax_registry)
    expected = f"{bulleted_list_delimiter}Item 1\n{bulleted_list_delimiter}Item 2\n{bulleted_list_delimiter}Item 3"

    assert bulleted_list.to_markdown() == expected


def test_empty_bulleted_list(syntax_registry: SyntaxDefinitionRegistry) -> None:
    bulleted_list = BulletedListMarkdownNode(texts=[], syntax_registry=syntax_registry)

    assert bulleted_list.to_markdown() == ""


def test_single_item_bulleted_list(syntax_registry: SyntaxDefinitionRegistry, bulleted_list_delimiter: str) -> None:
    bulleted_list = BulletedListMarkdownNode(texts=["Single item"], syntax_registry=syntax_registry)
    expected = f"{bulleted_list_delimiter}Single item"

    assert bulleted_list.to_markdown() == expected


def test_bulleted_list_with_paragraph_child(
    syntax_registry: SyntaxDefinitionRegistry, bulleted_list_delimiter: str, indent: str
) -> None:
    paragraph_child = ParagraphMarkdownNode(text="Child paragraph", syntax_registry=syntax_registry)
    bulleted_list = BulletedListMarkdownNode(
        texts=["Parent item"], children=[paragraph_child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()

    assert f"{bulleted_list_delimiter}Parent item" in result
    assert f"{indent}Child paragraph" in result


def test_bulleted_list_with_nested_list_child(
    syntax_registry: SyntaxDefinitionRegistry, bulleted_list_delimiter: str, indent: str
) -> None:
    nested_list = BulletedListMarkdownNode(texts=["Nested item 1", "Nested item 2"], syntax_registry=syntax_registry)
    parent_list = BulletedListMarkdownNode(
        texts=["Parent item"], children=[nested_list], syntax_registry=syntax_registry
    )

    result = parent_list.to_markdown()

    assert f"{bulleted_list_delimiter}Parent item" in result
    assert f"{indent}{bulleted_list_delimiter}Nested item 1" in result
    assert f"{indent}{bulleted_list_delimiter}Nested item 2" in result


def test_bulleted_list_with_multiple_items_and_children(
    syntax_registry: SyntaxDefinitionRegistry, bulleted_list_delimiter: str, indent: str
) -> None:
    first_child = ParagraphMarkdownNode(text="First child", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second child", syntax_registry=syntax_registry)
    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2"], children=[first_child, second_child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()

    assert f"{bulleted_list_delimiter}Item 1" in result
    assert f"{bulleted_list_delimiter}Item 2" in result
    assert f"{indent}First child" in result
    assert f"{indent}Second child" in result


def test_bulleted_list_with_fewer_children_than_items(
    syntax_registry: SyntaxDefinitionRegistry, bulleted_list_delimiter: str, indent: str
) -> None:
    child = ParagraphMarkdownNode(text="Only child", syntax_registry=syntax_registry)
    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2", "Item 3"], children=[child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()
    lines = result.split("\n")

    assert f"{bulleted_list_delimiter}Item 1" in lines[0]
    assert f"{indent}Only child" in lines[1]
    assert f"{bulleted_list_delimiter}Item 2" in lines[2]
    assert f"{bulleted_list_delimiter}Item 3" in lines[3]


def test_bulleted_list_with_none_children(
    syntax_registry: SyntaxDefinitionRegistry, bulleted_list_delimiter: str
) -> None:
    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2"], children=[None, None], syntax_registry=syntax_registry
    )
    expected = f"{bulleted_list_delimiter}Item 1\n{bulleted_list_delimiter}Item 2"

    result = bulleted_list.to_markdown()

    assert result == expected


def test_bulleted_list_children_order_preserved(syntax_registry: SyntaxDefinitionRegistry) -> None:
    first_child = ParagraphMarkdownNode(text="First", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second", syntax_registry=syntax_registry)
    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2"], children=[first_child, second_child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()
    first_position = result.index("First")
    second_position = result.index("Second")

    assert first_position < second_position
