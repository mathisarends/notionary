import pytest

from notionary.page.content.markdown.nodes import ImageMarkdownNode
from notionary.page.content.syntax import SyntaxDefinitionRegistry


@pytest.fixture
def image_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_image_syntax().start_delimiter


def test_image_without_caption(image_delimiter: str) -> None:
    image = ImageMarkdownNode(url="https://example.com/image.jpg")
    expected = f"{image_delimiter}https://example.com/image.jpg)"

    assert image.to_markdown() == expected


def test_image_with_caption(image_delimiter: str, caption_delimiter: str) -> None:
    image = ImageMarkdownNode(url="https://example.com/image.jpg", caption="My Image")
    expected = f"{image_delimiter}https://example.com/image.jpg)\n{caption_delimiter} My Image"

    assert image.to_markdown() == expected


def test_image_with_empty_caption(image_delimiter: str) -> None:
    image = ImageMarkdownNode(url="https://example.com/image.jpg", caption="")
    expected = f"{image_delimiter}https://example.com/image.jpg)"

    assert image.to_markdown() == expected
