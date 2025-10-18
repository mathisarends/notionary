from notionary.page.content.markdown.nodes import BulletedListMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


def test_simple_bulleted_list(syntax_registry: SyntaxRegistry) -> None:
    bulleted_list = BulletedListMarkdownNode(texts=["Item 1", "Item 2", "Item 3"], syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_bulleted_list_syntax().start_delimiter
    expected = f"{delimiter}Item 1\n{delimiter}Item 2\n{delimiter}Item 3"

    assert bulleted_list.to_markdown() == expected


def test_empty_bulleted_list(syntax_registry: SyntaxRegistry) -> None:
    bulleted_list = BulletedListMarkdownNode(texts=[], syntax_registry=syntax_registry)

    assert bulleted_list.to_markdown() == ""


def test_single_item_bulleted_list(syntax_registry: SyntaxRegistry) -> None:
    bulleted_list = BulletedListMarkdownNode(texts=["Single item"], syntax_registry=syntax_registry)

    delimiter = syntax_registry.get_bulleted_list_syntax().start_delimiter
    expected = f"{delimiter}Single item"

    assert bulleted_list.to_markdown() == expected


def test_bulleted_list_with_paragraph_child(syntax_registry: SyntaxRegistry) -> None:
    paragraph_child = ParagraphMarkdownNode(text="Child paragraph", syntax_registry=syntax_registry)

    bulleted_list = BulletedListMarkdownNode(
        texts=["Parent item"], children=[paragraph_child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()
    delimiter = syntax_registry.get_bulleted_list_syntax().start_delimiter

    assert f"{delimiter}Parent item" in result
    assert "    Child paragraph" in result


def test_bulleted_list_with_nested_list_child(syntax_registry: SyntaxRegistry) -> None:
    nested_list = BulletedListMarkdownNode(texts=["Nested item 1", "Nested item 2"], syntax_registry=syntax_registry)

    parent_list = BulletedListMarkdownNode(
        texts=["Parent item"], children=[nested_list], syntax_registry=syntax_registry
    )

    result = parent_list.to_markdown()
    delimiter = syntax_registry.get_bulleted_list_syntax().start_delimiter

    assert f"{delimiter}Parent item" in result
    assert f"    {delimiter}Nested item 1" in result
    assert f"    {delimiter}Nested item 2" in result


def test_bulleted_list_with_multiple_items_and_children(syntax_registry: SyntaxRegistry) -> None:
    first_child = ParagraphMarkdownNode(text="First child", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second child", syntax_registry=syntax_registry)

    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2"], children=[first_child, second_child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()
    delimiter = syntax_registry.get_bulleted_list_syntax().start_delimiter

    assert f"{delimiter}Item 1" in result
    assert f"{delimiter}Item 2" in result
    assert "    First child" in result
    assert "    Second child" in result


def test_bulleted_list_with_fewer_children_than_items(syntax_registry: SyntaxRegistry) -> None:
    child = ParagraphMarkdownNode(text="Only child", syntax_registry=syntax_registry)

    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2", "Item 3"], children=[child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()
    delimiter = syntax_registry.get_bulleted_list_syntax().start_delimiter

    lines = result.split("\n")
    assert f"{delimiter}Item 1" in lines[0]
    assert "    Only child" in lines[1]
    assert f"{delimiter}Item 2" in lines[2]
    assert f"{delimiter}Item 3" in lines[3]


def test_bulleted_list_with_none_children(syntax_registry: SyntaxRegistry) -> None:
    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2"], children=[None, None], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()
    delimiter = syntax_registry.get_bulleted_list_syntax().start_delimiter
    expected = f"{delimiter}Item 1\n{delimiter}Item 2"

    assert result == expected


def test_bulleted_list_children_order_preserved(syntax_registry: SyntaxRegistry) -> None:
    first_child = ParagraphMarkdownNode(text="First", syntax_registry=syntax_registry)
    second_child = ParagraphMarkdownNode(text="Second", syntax_registry=syntax_registry)

    bulleted_list = BulletedListMarkdownNode(
        texts=["Item 1", "Item 2"], children=[first_child, second_child], syntax_registry=syntax_registry
    )

    result = bulleted_list.to_markdown()
    first_position = result.index("First")
    second_position = result.index("Second")

    assert first_position < second_position
