import pytest

from notionary.page.content.markdown.nodes import HeadingMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry


@pytest.fixture
def heading_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_heading_syntax().start_delimiter


def test_heading_level_1(heading_delimiter: str) -> None:
    heading = HeadingMarkdownNode(text="Heading 1", level=1)
    expected = f"{heading_delimiter} Heading 1"

    assert heading.to_markdown() == expected


def test_heading_level_2(heading_delimiter: str) -> None:
    heading = HeadingMarkdownNode(text="Heading 2", level=2)
    expected = f"{heading_delimiter * 2} Heading 2"

    assert heading.to_markdown() == expected


def test_heading_level_3(heading_delimiter: str) -> None:
    heading = HeadingMarkdownNode(text="Heading 3", level=3)
    expected = f"{heading_delimiter * 3} Heading 3"

    assert heading.to_markdown() == expected


def test_heading_level_4_clamped(heading_delimiter: str) -> None:
    heading = HeadingMarkdownNode(text="still valid", level=4)
    expected = f"{heading_delimiter * 3} still valid"

    assert heading.to_markdown() == expected


def test_heading_with_children(heading_delimiter: str, indent: str) -> None:
    child1 = ParagraphMarkdownNode(text="First paragraph")
    child2 = ParagraphMarkdownNode(text="Second paragraph")
    heading = HeadingMarkdownNode(
        text="Toggleable Heading",
        level=2,
        children=[child1, child2],
    )

    result = heading.to_markdown()

    assert f"{heading_delimiter * 2} Toggleable Heading" in result
    assert f"{indent}First paragraph" in result
    assert f"{indent}Second paragraph" in result
