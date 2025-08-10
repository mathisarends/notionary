"""
Minimal tests for ImageElement.
Tests core functionality for image embeds ([image](url)).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.image_block.image_element import ImageElement
from notionary.blocks.image_block.image_models import CreateImageBlock
from notionary.blocks.paragraph.paragraph_models import CreateParagraphBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject


def test_match_markdown_valid():
    """Test recognition of valid image formats."""
    assert ImageElement.match_markdown("[image](https://example.com/pic.jpg)")
    assert ImageElement.match_markdown('[image](https://test.com/img.png "Caption")')
    assert ImageElement.match_markdown("[image](http://site.org/photo.gif)")
    assert ImageElement.match_markdown("  [image](https://example.com/img.jpg)  ")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not ImageElement.match_markdown(
        "[img](https://example.com/pic.jpg)"
    )  # Wrong prefix
    assert not ImageElement.match_markdown("[image](not-a-url)")  # Invalid URL
    assert not ImageElement.match_markdown("[image]()")  # Empty URL
    assert not ImageElement.match_markdown("Regular text")
    assert not ImageElement.match_markdown("")


def test_match_notion():
    """Test recognition of Notion image blocks."""
    # Valid image block
    image_block = Mock()
    image_block.type = "image"
    image_block.image = Mock()  # Not None
    assert ImageElement.match_notion(image_block)

    # Invalid blocks
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.image = None
    assert not ImageElement.match_notion(paragraph_block)

    # Image type but image is None
    empty_image_block = Mock()
    empty_image_block.type = "image"
    empty_image_block.image = None
    assert not ImageElement.match_notion(empty_image_block)


def test_markdown_to_notion_without_caption():
    """Test conversion from markdown to Notion without caption."""
    result = ImageElement.markdown_to_notion("[image](https://example.com/pic.jpg)")

    assert result is not None
    assert len(result) == 2  # Image block + empty paragraph

    # Check image block
    image_block = result[0]
    assert isinstance(image_block, CreateImageBlock)
    assert image_block.type == "image"
    assert image_block.image.type == "external"
    assert image_block.image.external.url == "https://example.com/pic.jpg"
    assert image_block.image.caption == []

    # Check empty paragraph
    paragraph_block = result[1]
    assert isinstance(paragraph_block, CreateParagraphBlock)
    assert paragraph_block.paragraph.rich_text == []


def test_markdown_to_notion_with_caption():
    """Test conversion from markdown to Notion with caption."""
    result = ImageElement.markdown_to_notion(
        '[image](https://example.com/pic.jpg "My Photo")'
    )

    assert result is not None
    image_block = result[0]

    assert isinstance(image_block, CreateImageBlock)
    assert image_block.image.external.url == "https://example.com/pic.jpg"
    assert len(image_block.image.caption) == 1
    assert image_block.image.caption[0].plain_text == "My Photo"


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert ImageElement.markdown_to_notion("[img](https://example.com/pic.jpg)") is None
    assert ImageElement.markdown_to_notion("[image]()") is None
    assert ImageElement.markdown_to_notion("text") is None


def test_notion_to_markdown_external_without_caption():
    """Test conversion from Notion to markdown (external file, no caption)."""
    # Mock external file block
    block = Mock()
    block.type = "image"
    block.image = Mock()
    block.image.type = "external"
    block.image.external = Mock()
    block.image.external.url = "https://example.com/image.png"
    block.image.caption = []

    result = ImageElement.notion_to_markdown(block)
    assert result == "[image](https://example.com/image.png)"


def test_notion_to_markdown_external_with_caption():
    """Test conversion from Notion to markdown (external file, with caption)."""
    # Mock external file block with caption
    block = Mock()
    block.type = "image"
    block.image = Mock()
    block.image.type = "external"
    block.image.external = Mock()
    block.image.external.url = "https://example.com/photo.jpg"

    # Mock caption with real RichTextObject
    caption_rt = RichTextObject.from_plain_text("Beautiful sunset")
    block.image.caption = [caption_rt]

    result = ImageElement.notion_to_markdown(block)
    assert result == '[image](https://example.com/photo.jpg "Beautiful sunset")'


def test_notion_to_markdown_notion_hosted():
    """Test conversion from Notion-hosted file."""
    # Mock notion-hosted file
    block = Mock()
    block.type = "image"
    block.image = Mock()
    block.image.type = "file"
    block.image.external = None
    block.image.file = Mock()
    block.image.file.url = "https://notion.s3.amazonaws.com/image123.png"
    block.image.caption = []

    result = ImageElement.notion_to_markdown(block)
    assert result == "[image](https://notion.s3.amazonaws.com/image123.png)"


def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.image = None
    assert ImageElement.notion_to_markdown(paragraph_block) is None

    # No image content
    image_block = Mock()
    image_block.type = "image"
    image_block.image = None
    assert ImageElement.notion_to_markdown(image_block) is None

    # Unsupported file type
    upload_block = Mock()
    upload_block.type = "image"
    upload_block.image = Mock()
    upload_block.image.type = "file_upload"
    upload_block.image.external = None
    upload_block.image.file = None
    assert ImageElement.notion_to_markdown(upload_block) is None


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("[image](https://example.com/pic.jpg)", True),
        ('[image](https://test.com/img.png "Caption")', True),
        ("[image](http://site.org/photo.gif)", True),
        ("  [image](https://example.com/img.jpg)  ", True),  # With whitespace
        ("[img](https://example.com/pic.jpg)", False),  # Wrong prefix
        ("[image](not-a-url)", False),  # Invalid URL
        ("[image]()", False),  # Empty URL
        ("Regular text", False),
        ("", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test various markdown patterns."""
    result = ImageElement.match_markdown(markdown)
    assert result == should_match


def test_pattern_matching():
    """Test the regex pattern directly."""
    pattern = ImageElement.PATTERN

    # Valid patterns
    assert pattern.match("[image](https://example.com/pic.jpg)")
    assert pattern.match('[image](https://test.com/img.png "Caption")')

    # Invalid patterns
    assert not pattern.match("[img](https://example.com/pic.jpg)")
    assert not pattern.match("[image](not-a-url)")
    assert not pattern.match("[image]()")


def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "[image](https://example.com/image.jpg)",
        '[image](https://example.com/photo.png "Sunset")',
        "[image](http://site.org/diagram.gif)",
    ]

    for markdown in test_cases:
        # Convert to notion
        notion_result = ImageElement.markdown_to_notion(markdown)
        assert notion_result is not None

        # Create mock block for notion_to_markdown
        image_create_block = notion_result[0]
        block = Mock()
        block.type = "image"
        block.image = image_create_block.image

        # Convert back to markdown
        result = ImageElement.notion_to_markdown(block)
        assert result == markdown


def test_caption_with_special_characters():
    """Test captions with special characters."""
    markdown = '[image](https://example.com/pic.jpg "Photo with ümlaut & emoji 🌅")'
    result = ImageElement.markdown_to_notion(markdown)

    assert result is not None
    image_block = result[0]
    caption_text = image_block.image.caption[0].plain_text
    assert caption_text == "Photo with ümlaut & emoji 🌅"


def test_multiple_caption_parts():
    """Test notion_to_markdown with multiple rich text objects in caption."""
    block = Mock()
    block.type = "image"
    block.image = Mock()
    block.image.type = "external"
    block.image.external = Mock()
    block.image.external.url = "https://example.com/pic.jpg"

    # Multiple rich text objects in caption
    rt1 = RichTextObject.from_plain_text("Part 1 ")
    rt2 = RichTextObject.from_plain_text("Part 2")
    block.image.caption = [rt1, rt2]

    result = ImageElement.notion_to_markdown(block)
    assert result == '[image](https://example.com/pic.jpg "Part 1 Part 2")'