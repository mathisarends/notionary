from notionary.blocks.markdown.nodes import HeadingMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_heading_markdown_node() -> None:
    registry = SyntaxRegistry()
    heading_syntax = registry.get_heading_syntax()

    h1 = HeadingMarkdownNode(text="Heading 1", level=1)
    expected = f"{heading_syntax.start_delimiter} Heading 1"
    assert h1.to_markdown() == expected

    h2 = HeadingMarkdownNode(text="Heading 2", level=2)
    expected = f"{heading_syntax.start_delimiter * 2} Heading 2"
    assert h2.to_markdown() == expected

    h3 = HeadingMarkdownNode(text="Heading 3", level=3)
    expected = f"{heading_syntax.start_delimiter * 3} Heading 3"
    assert h3.to_markdown() == expected

    # Level wird jetzt geclampt, wirft keine ValueError mehr
    h4_clamped = HeadingMarkdownNode(text="Invalid", level=4)
    expected = f"{heading_syntax.start_delimiter * 3} Invalid"  # Clamped to 3
    assert h4_clamped.to_markdown() == expected
