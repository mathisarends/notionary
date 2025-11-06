import pytest

from notionary.page.content.syntax.definition import MarkdownGrammar


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()
