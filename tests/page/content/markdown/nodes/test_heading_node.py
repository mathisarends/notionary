from notionary.page.content.markdown.nodes import HeadingMarkdownNode, ParagraphMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_heading_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    heading_syntax = syntax_registry.get_heading_syntax()

    h1 = HeadingMarkdownNode(text="Heading 1", level=1)
    expected = f"{heading_syntax.start_delimiter} Heading 1"
    assert h1.to_markdown() == expected

    h2 = HeadingMarkdownNode(text="Heading 2", level=2)
    expected = f"{heading_syntax.start_delimiter * 2} Heading 2"
    assert h2.to_markdown() == expected

    h3 = HeadingMarkdownNode(text="Heading 3", level=3)
    expected = f"{heading_syntax.start_delimiter * 3} Heading 3"
    assert h3.to_markdown() == expected

    h4_clamped = HeadingMarkdownNode(text="still valid", level=4)
    expected = f"{heading_syntax.start_delimiter * 3} still valid"
    assert h4_clamped.to_markdown() == expected


def test_heading_with_children(syntax_registry: SyntaxRegistry) -> None:
    """Test heading with nested children using indentation (toggleable)."""
    heading_syntax = syntax_registry.get_heading_syntax()

    # Create children
    child1 = ParagraphMarkdownNode(text="First paragraph")
    child2 = ParagraphMarkdownNode(text="Second paragraph")

    heading = HeadingMarkdownNode(
        text="Toggleable Heading",
        level=2,
        children=[child1, child2],
    )

    result = heading.to_markdown()

    # Check parent heading
    assert f"{heading_syntax.start_delimiter * 2} Toggleable Heading" in result

    # Check indented children (4 spaces)
    assert "    First paragraph" in result
    assert "    Second paragraph" in result
