from notionary.blocks.markdown.nodes import CodeMarkdownNode
from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.page.content.syntax.service import SyntaxRegistry


def test_code_markdown_node(syntax_registry: SyntaxRegistry, caption_syntax: SyntaxDefinition) -> None:
    code_syntax = syntax_registry.get_code_syntax()

    code = CodeMarkdownNode(code="print('Hello World')")
    expected = f"{code_syntax.start_delimiter}\nprint('Hello World')\n{code_syntax.end_delimiter}"
    assert code.to_markdown() == expected

    code_with_lang = CodeMarkdownNode(code="print('Hello World')", language="python")
    expected = f"{code_syntax.start_delimiter}python\nprint('Hello World')\n{code_syntax.end_delimiter}"
    assert code_with_lang.to_markdown() == expected

    code_with_caption = CodeMarkdownNode(code="print('Hello World')", language="python", caption="Example code")
    expected = f"{code_syntax.start_delimiter}python\nprint('Hello World')\n{code_syntax.end_delimiter}\n{caption_syntax.start_delimiter} Example code"
    assert code_with_caption.to_markdown() == expected
