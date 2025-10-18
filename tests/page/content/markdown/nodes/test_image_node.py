from notionary.page.content.markdown.nodes import ImageMarkdownNode
from notionary.page.content.syntax import SyntaxRegistry
from notionary.page.content.syntax.models import SyntaxDefinition


def test_image_markdown_node(syntax_registry: SyntaxRegistry, caption_syntax: SyntaxDefinition) -> None:
    image_syntax = syntax_registry.get_image_syntax()

    image = ImageMarkdownNode(url="https://example.com/image.jpg")
    expected = f"{image_syntax.start_delimiter}https://example.com/image.jpg)"
    assert image.to_markdown() == expected

    image_with_caption = ImageMarkdownNode(url="https://example.com/image.jpg", caption="My Image")
    expected = (
        f"{image_syntax.start_delimiter}https://example.com/image.jpg)\n{caption_syntax.start_delimiter} My Image"
    )
    assert image_with_caption.to_markdown() == expected

    image_empty = ImageMarkdownNode(url="https://example.com/image.jpg", caption="")
    expected = f"{image_syntax.start_delimiter}https://example.com/image.jpg)"
    assert image_empty.to_markdown() == expected
