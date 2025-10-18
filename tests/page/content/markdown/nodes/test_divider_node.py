import pytest

from notionary.page.content.markdown.nodes import DividerMarkdownNode
from notionary.page.content.syntax import SyntaxRegistry


@pytest.fixture
def divider_delimiter(syntax_registry: SyntaxRegistry) -> str:
    return syntax_registry.get_divider_syntax().start_delimiter


def test_divider_markdown_node(divider_delimiter: str) -> None:
    divider = DividerMarkdownNode()
    expected = divider_delimiter

    assert divider.to_markdown() == expected
