from notionary.page.content.markdown.nodes import (
    ParagraphMarkdownNode,
    ToggleMarkdownNode,
)
from notionary.page.content.syntax.service import SyntaxRegistry


def test_toggle_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    toggle_syntax = syntax_registry.get_toggle_syntax()

    toggle = ToggleMarkdownNode(title="Details", children=[])
    expected = f"{toggle_syntax.start_delimiter} Details\n{toggle_syntax.end_delimiter}"
    assert toggle.to_markdown() == expected

    line1_node = ParagraphMarkdownNode(text="Line 1")
    line2_node = ParagraphMarkdownNode(text="Line 2")

    toggle_with_content = ToggleMarkdownNode(
        title="More Info",
        children=[line1_node, line2_node],
    )
    expected = f"{toggle_syntax.start_delimiter} More Info\nLine 1\n\nLine 2\n{toggle_syntax.end_delimiter}"
    assert toggle_with_content.to_markdown() == expected
