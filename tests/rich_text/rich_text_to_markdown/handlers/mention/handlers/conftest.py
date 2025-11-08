import pytest

from notionary.markdown.syntax.definition import MarkdownGrammar


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()
