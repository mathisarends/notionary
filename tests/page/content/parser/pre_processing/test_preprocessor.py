from notionary.page.content.parser.pre_processsing.handlers.column_syntax import (
    ColumnSyntaxPreProcessor,
)
from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor
from notionary.page.content.parser.pre_processsing.handlers.whitespace import (
    WhitespacePreProcessor,
)
from notionary.page.content.parser.pre_processsing.service import MarkdownPreProcessor


class UpperCasePreProcessor(PreProcessor):
    def process(self, markdown_text: str) -> str:
        return markdown_text.upper()


class PrefixPreProcessor(PreProcessor):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def process(self, markdown_text: str) -> str:
        return f"{self.prefix}{markdown_text}"


def test_preprocessor_service_empty_should_return_unchanged() -> None:
    service = MarkdownPreProcessor()
    text = "Hello World"

    result = service.process(text)

    assert result == text


def test_preprocessor_service_single_processor() -> None:
    service = MarkdownPreProcessor()
    service.register(UpperCasePreProcessor())

    result = service.process("hello")

    assert result == "HELLO"


def test_preprocessor_service_multiple_processors_execute_in_order() -> None:
    service = MarkdownPreProcessor()
    service.register(PrefixPreProcessor(">>> "))
    service.register(UpperCasePreProcessor())

    result = service.process("test")

    assert result == ">>> TEST"


def test_preprocessor_service_with_whitespace_processor() -> None:
    service = MarkdownPreProcessor()
    service.register(WhitespacePreProcessor())

    markdown = """
        # Heading
            Indented text
    """

    result = service.process(markdown)

    assert "# Heading" in result
    assert "Indented text" in result
    # Leading whitespace should be removed
    assert not result.startswith(" ")


def test_preprocessor_service_with_column_syntax_processor() -> None:
    service = MarkdownPreProcessor()
    service.register(ColumnSyntaxPreProcessor())

    markdown = """
::: columns
::: column
Left
:::

::: column
Right
:::
:::
    """

    result = service.process(markdown)
    assert result == markdown


def test_preprocessor_service_chain_whitespace_and_column() -> None:
    service = MarkdownPreProcessor()
    service.register(WhitespacePreProcessor())
    service.register(ColumnSyntaxPreProcessor())

    markdown = """
        ::: columns
        ::: column
        Left content
        :::

        ::: column
        Right content
        :::
        :::
    """

    result = service.process(markdown)

    assert "::: columns" in result
    assert "Left content" in result
    assert "Right content" in result
