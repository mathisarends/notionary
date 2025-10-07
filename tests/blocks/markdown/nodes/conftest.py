import pytest

from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def syntax_registry() -> SyntaxRegistry:
    return SyntaxRegistry()


@pytest.fixture
def image_syntax(syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
    return syntax_registry.get_image_syntax()


@pytest.fixture
def caption_syntax(syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
    return syntax_registry.get_caption_syntax()


@pytest.fixture
def table_syntax(syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
    return syntax_registry.get_table_syntax()


@pytest.fixture
def code_syntax(syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
    return syntax_registry.get_code_syntax()
