import pytest

from notionary.page.content.syntax import SyntaxRegistry
from notionary.page.content.syntax.grammar import MarkdownGrammar


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def indent(markdown_grammar: MarkdownGrammar) -> str:
    return " " * markdown_grammar.spaces_per_nesting_level


@pytest.fixture
def syntax_registry() -> SyntaxRegistry:
    return SyntaxRegistry()
