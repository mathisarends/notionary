import pytest

from notionary.page.content.syntax import MarkdownGrammar, SyntaxRegistry
from notionary.page.content.syntax.models import SyntaxDefinition


@pytest.fixture
def syntax_registry() -> SyntaxRegistry:
    return SyntaxRegistry()


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def indent(markdown_grammar: MarkdownGrammar) -> str:
    return " " * markdown_grammar.spaces_per_nesting_level


@pytest.fixture
def caption_syntax(syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
    return syntax_registry.get_caption_syntax()
