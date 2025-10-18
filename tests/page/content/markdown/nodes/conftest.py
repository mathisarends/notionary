import pytest

from notionary.page.content.syntax import SyntaxRegistry
from notionary.page.content.syntax.models import SyntaxDefinition


@pytest.fixture
def syntax_registry() -> SyntaxRegistry:
    return SyntaxRegistry()


@pytest.fixture
def caption_syntax(syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
    return syntax_registry.get_caption_syntax()
