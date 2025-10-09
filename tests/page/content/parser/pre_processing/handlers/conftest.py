import pytest

from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def syntax_registry() -> SyntaxRegistry:
    """Provides a SyntaxRegistry instance for tests."""
    return SyntaxRegistry()
