from notionary.blocks.markdown.nodes import ImageMarkdownNode


def test_image_markdown_node() -> None:
    """Test ImageMarkdownNode"""
    image = ImageMarkdownNode(url="https://example.com/image.jpg")
    expected = "[image](https://example.com/image.jpg)"
    assert image.to_markdown() == expected

    image_with_caption = ImageMarkdownNode(url="https://example.com/image.jpg", caption="My Image")
    expected = "[image](https://example.com/image.jpg)(caption:My Image)"
    assert image_with_caption.to_markdown() == expected

    image_full = ImageMarkdownNode(url="https://example.com/image.jpg", caption="My Image", alt="Alternative text")
    expected = "[image](https://example.com/image.jpg)(caption:My Image)"
    assert image_full.to_markdown() == expected

    image_empty = ImageMarkdownNode(url="https://example.com/image.jpg", caption="")
    expected = "[image](https://example.com/image.jpg)"
    assert image_empty.to_markdown() == expected
