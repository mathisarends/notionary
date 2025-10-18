from notionary.page.content.markdown.nodes import (
    ParagraphMarkdownNode,
    ToggleableHeadingMarkdownNode,
)
from notionary.page.content.syntax import SyntaxRegistry


def test_toggleable_heading_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    toggle_syntax = syntax_registry.get_toggle_syntax()
    heading_syntax = syntax_registry.get_heading_syntax()

    toggleable_h1 = ToggleableHeadingMarkdownNode(text="Section 1", level=1, children=[])
    expected = (
        f"{toggle_syntax.start_delimiter}{heading_syntax.start_delimiter} Section 1\n{toggle_syntax.end_delimiter}"
    )
    assert toggleable_h1.to_markdown() == expected

    # Test mit Content - korrekte Syntax mit +++
    toggleable_h2 = ToggleableHeadingMarkdownNode(
        text="Section 2",
        level=2,
        children=[
            ParagraphMarkdownNode(text="Content line 1"),
            ParagraphMarkdownNode(text="Content line 2"),
        ],
    )
    expected = f"{toggle_syntax.start_delimiter}{heading_syntax.start_delimiter * 2} Section 2\nContent line 1\n\nContent line 2\n{toggle_syntax.end_delimiter}"
    assert toggleable_h2.to_markdown() == expected

    # Level wird jetzt geclampt, wirft keine ValueError mehr
    toggleable_h4_clamped = ToggleableHeadingMarkdownNode(text="Invalid", level=4, children=[])
    expected = f"{toggle_syntax.start_delimiter}{heading_syntax.start_delimiter * 3} Invalid\n{toggle_syntax.end_delimiter}"  # Clamped to 3
    assert toggleable_h4_clamped.to_markdown() == expected
