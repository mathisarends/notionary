import pytest

from notionary.blocks.enums import CodingLanguage
from notionary.page.content.markdown.nodes import CodeMarkdownNode
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.page.content.syntax.definition.models import SyntaxDefinition


@pytest.fixture
def code_syntax(syntax_registry: SyntaxDefinitionRegistry) -> SyntaxDefinition:
    return syntax_registry.get_code_syntax()


@pytest.fixture
def code_start_delimiter(code_syntax: SyntaxDefinition) -> str:
    return code_syntax.start_delimiter


@pytest.fixture
def code_end_delimiter(code_syntax: SyntaxDefinition) -> str:
    return code_syntax.end_delimiter


def test_code_without_language(code_start_delimiter: str, code_end_delimiter: str) -> None:
    code = CodeMarkdownNode(code="print('Hello World')")
    expected = f"{code_start_delimiter}\nprint('Hello World')\n{code_end_delimiter}"

    assert code.to_markdown() == expected


def test_code_with_language(code_start_delimiter: str, code_end_delimiter: str) -> None:
    code = CodeMarkdownNode(code="print('Hello World')", language=CodingLanguage.PYTHON)
    expected = f"{code_start_delimiter}python\nprint('Hello World')\n{code_end_delimiter}"

    assert code.to_markdown() == expected


def test_code_with_caption(code_start_delimiter: str, code_end_delimiter: str, caption_delimiter: str) -> None:
    code = CodeMarkdownNode(code="print('Hello World')", language=CodingLanguage.PYTHON, caption="Example code")
    expected = (
        f"{code_start_delimiter}python\nprint('Hello World')\n{code_end_delimiter}\n{caption_delimiter} Example code"
    )

    assert code.to_markdown() == expected
