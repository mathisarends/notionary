import pytest

from notionary.page.content.syntax import SyntaxRegistry


@pytest.fixture
def syntax_registry() -> SyntaxRegistry:
    return SyntaxRegistry()
