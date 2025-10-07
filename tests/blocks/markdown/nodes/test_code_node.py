from notionary.blocks.markdown.nodes import CodeMarkdownNode


def test_code_markdown_node() -> None:
    code = CodeMarkdownNode(code="print('Hello World')")
    expected = "```\nprint('Hello World')\n```"
    assert code.to_markdown() == expected

    code_with_lang = CodeMarkdownNode(code="print('Hello World')", language="python")
    expected = "```python\nprint('Hello World')\n```"
    assert code_with_lang.to_markdown() == expected

    code_with_caption = CodeMarkdownNode(code="print('Hello World')", language="python", caption="Example code")
    expected = "```python \"Example code\"\nprint('Hello World')\n```"
    assert code_with_caption.to_markdown() == expected
