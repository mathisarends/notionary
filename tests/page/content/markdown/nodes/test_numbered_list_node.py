from notionary.page.content.markdown.nodes import (
    NumberedListMarkdownNode,
    ParagraphMarkdownNode,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


def test_simple_numbered_list(syntax_registry: SyntaxDefinitionRegistry) -> None:
    numbered_list = NumberedListMarkdownNode(
        texts=["First", "Second", "Third"], syntax_registry=syntax_registry
    )
    expected = "1. First\n2. Second\n3. Third"

    assert numbered_list.to_markdown() == expected


def test_empty_numbered_list(syntax_registry: SyntaxDefinitionRegistry) -> None:
    numbered_list = NumberedListMarkdownNode(texts=[], syntax_registry=syntax_registry)

    assert numbered_list.to_markdown() == ""


def test_single_item_numbered_list(syntax_registry: SyntaxDefinitionRegistry) -> None:
    numbered_list = NumberedListMarkdownNode(
        texts=["Only item"], syntax_registry=syntax_registry
    )
    expected = "1. Only item"

    assert numbered_list.to_markdown() == expected


def test_numbered_list_with_paragraph_child(
    syntax_registry: SyntaxDefinitionRegistry, indent: str
) -> None:
    paragraph_child = ParagraphMarkdownNode(
        text="Nested explanation", syntax_registry=syntax_registry
    )
    numbered_list = NumberedListMarkdownNode(
        texts=["First item"],
        children=[paragraph_child],
        syntax_registry=syntax_registry,
    )

    result = numbered_list.to_markdown()

    assert "1. First item" in result
    assert f"{indent}Nested explanation" in result


def test_numbered_list_with_nested_list_child(
    syntax_registry: SyntaxDefinitionRegistry, indent: str
) -> None:
    nested_list = NumberedListMarkdownNode(
        texts=["Sub-item 1", "Sub-item 2"], syntax_registry=syntax_registry
    )
    parent_list = NumberedListMarkdownNode(
        texts=["Parent item"], children=[nested_list], syntax_registry=syntax_registry
    )

    result = parent_list.to_markdown()

    assert "1. Parent item" in result
    assert f"{indent}1. Sub-item 1" in result
    assert f"{indent}2. Sub-item 2" in result


def test_numbered_list_with_multiple_items_and_children(
    syntax_registry: SyntaxDefinitionRegistry, indent: str
) -> None:
    first_child = ParagraphMarkdownNode(
        text="First explanation", syntax_registry=syntax_registry
    )
    second_child = ParagraphMarkdownNode(
        text="Second explanation", syntax_registry=syntax_registry
    )
    numbered_list = NumberedListMarkdownNode(
        texts=["Item 1", "Item 2"],
        children=[first_child, second_child],
        syntax_registry=syntax_registry,
    )

    result = numbered_list.to_markdown()

    assert "1. Item 1" in result
    assert "2. Item 2" in result
    assert f"{indent}First explanation" in result
    assert f"{indent}Second explanation" in result


def test_numbered_list_with_fewer_children_than_items(
    syntax_registry: SyntaxDefinitionRegistry, indent: str
) -> None:
    child = ParagraphMarkdownNode(text="Only child", syntax_registry=syntax_registry)
    numbered_list = NumberedListMarkdownNode(
        texts=["Item 1", "Item 2", "Item 3"],
        children=[child],
        syntax_registry=syntax_registry,
    )

    result = numbered_list.to_markdown()
    lines = result.split("\n")

    assert "1. Item 1" in lines[0]
    assert f"{indent}Only child" in lines[1]
    assert "2. Item 2" in lines[2]
    assert "3. Item 3" in lines[3]


def test_numbered_list_with_none_children(
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    numbered_list = NumberedListMarkdownNode(
        texts=["Item 1", "Item 2"],
        children=[None, None],
        syntax_registry=syntax_registry,
    )
    expected = "1. Item 1\n2. Item 2"

    result = numbered_list.to_markdown()

    assert result == expected


def test_numbered_list_children_order_preserved(
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    first_child = ParagraphMarkdownNode(text="First", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second", syntax_registry=syntax_registry)
    numbered_list = NumberedListMarkdownNode(
        texts=["Item 1", "Item 2"],
        children=[first_child, second_child],
        syntax_registry=syntax_registry,
    )

    result = numbered_list.to_markdown()
    first_position = result.index("First")
    second_position = result.index("Second")

    assert first_position < second_position


def test_numbered_list_numbering_starts_at_one(
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    numbered_list = NumberedListMarkdownNode(
        texts=["Alpha", "Beta", "Gamma"], syntax_registry=syntax_registry
    )

    result = numbered_list.to_markdown()

    assert result.startswith("1. ")
    assert "2. " in result
    assert "3. " in result
    assert "0. " not in result


def test_numbered_list_with_ten_items(
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    texts = [f"Item {i}" for i in range(1, 11)]
    numbered_list = NumberedListMarkdownNode(
        texts=texts, syntax_registry=syntax_registry
    )

    result = numbered_list.to_markdown()

    for i in range(1, 11):
        assert f"{i}. Item {i}" in result
