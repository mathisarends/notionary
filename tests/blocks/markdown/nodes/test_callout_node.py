from notionary.blocks.markdown.nodes import CalloutMarkdownNode


def test_callout_markdown_node() -> None:
    callout = CalloutMarkdownNode(text="This is important")
    expected = "::: callout\nThis is important\n:::"
    assert callout.to_markdown() == expected

    callout_with_emoji = CalloutMarkdownNode(text="Warning!", emoji="⚠️")
    expected = "::: callout ⚠️\nWarning!\n:::"
    assert callout_with_emoji.to_markdown() == expected
