import pytest

from notionary.page.content.syntax.definition import (
    MarkdownGrammar,
    SyntaxDefinitionRegistry,
)
from notionary.page.content.syntax.definition.models import SyntaxDefinition


@pytest.fixture
def syntax_registry() -> SyntaxDefinitionRegistry:
    return SyntaxDefinitionRegistry()


@pytest.fixture
def markdown_grammar() -> MarkdownGrammar:
    return MarkdownGrammar()


@pytest.fixture
def indent(markdown_grammar: MarkdownGrammar) -> str:
    return " " * markdown_grammar.spaces_per_nesting_level


@pytest.fixture
def caption_syntax(syntax_registry: SyntaxDefinitionRegistry) -> SyntaxDefinition:
    return syntax_registry.get_caption_syntax()


@pytest.fixture
def caption_delimiter(caption_syntax: SyntaxDefinition) -> str:
    return caption_syntax.start_delimiter
