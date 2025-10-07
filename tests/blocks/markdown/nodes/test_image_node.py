from notionary.blocks.markdown.nodes import ImageMarkdownNode
from notionary.page.content.syntax.service import SyntaxRegistry


def test_image_markdown_node() -> None:
    registry = SyntaxRegistry()
    image_syntax = registry.get_image_syntax()
    caption_syntax = registry.get_caption_syntax()

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
