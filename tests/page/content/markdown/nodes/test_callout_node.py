from notionary.page.content.markdown.nodes import CalloutMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_callout_markdown_node(syntax_registry: SyntaxRegistry) -> None:
    callout_syntax = syntax_registry.get_callout_syntax()

    # Test without emoji
    callout = CalloutMarkdownNode(text="This is important")
    expected = f"{callout_syntax.start_delimiter}This is important{callout_syntax.end_delimiter}"
    assert callout.to_markdown() == expected

    # Test with emoji
    callout_with_emoji = CalloutMarkdownNode(text="Warning!", emoji="⚠️")
    expected = f'{callout_syntax.start_delimiter}Warning! "⚠️"{callout_syntax.end_delimiter}'
    assert callout_with_emoji.to_markdown() == expected
