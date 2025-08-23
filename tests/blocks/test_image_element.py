"""
Minimal tests for ImageElement.
Tests core functionality for image embeds ([image](url)).
"""

from unittest.mock import Mock

import pytest

from notionary.blocks.image_block.image_element import ImageElement
from notionary.blocks.image_block.image_models import CreateImageBlock
from notionary.blocks.paragraph.paragraph_models import CreateParagraphBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid image formats."""
    assert await ImageElement.markdown_to_notion("[image](https://example.com/pic.jpg)")
    assert await ImageElement.markdown_to_notion(
        "[image](https://test.com/img.png)(caption:Caption)"
    )
    assert await ImageElement.markdown_to_notion("[image](http://site.org/photo.gif)")
    assert await ImageElement.markdown_to_notion(
        "  [image](https://example.com/img.jpg)  "
    )


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not await ImageElement.markdown_to_notion(
        "[img](https://example.com/pic.jpg)"
    )  # Wrong prefix
    assert not await ImageElement.markdown_to_notion(
        "[image](not-a-url)"
    )  # Invalid URL
    assert not await ImageElement.markdown_to_notion("[image]()")  # Empty URL
    assert await ImageElement.markdown_to_notion("Regular text") is None
    assert await ImageElement.markdown_to_notion("") is None


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


@pytest.mark.asyncio
async def test_markdown_to_notion_without_caption():
    """Test conversion from markdown to Notion without caption."""
    result = await ImageElement.markdown_to_notion(
        "[image](https://example.com/pic.jpg)"
    )

    assert result is not None

    # Check image block
    image_block = result
    assert isinstance(image_block, CreateImageBlock)
    assert image_block.type == "image"
    assert image_block.image.type == "external"
    assert image_block.image.external.url == "https://example.com/pic.jpg"
    assert image_block.image.caption == []


@pytest.mark.asyncio
async def test_markdown_to_notion_with_caption():
    """Test conversion from markdown to Notion with caption."""
    result = await ImageElement.markdown_to_notion(
        "[image](https://example.com/pic.jpg)(caption:My Photo)"
    )

    assert result is not None
    image_block = result

    assert isinstance(image_block, CreateImageBlock)
    assert image_block.image.external.url == "https://example.com/pic.jpg"
    assert len(image_block.image.caption) == 1
    assert image_block.image.caption[0].plain_text == "My Photo"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert (
        await ImageElement.markdown_to_notion("[img](https://example.com/pic.jpg)")
        is None
    )
    assert await ImageElement.markdown_to_notion("[image]()") is None
    assert await ImageElement.markdown_to_notion("text") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_external_without_caption():
    """Test conversion from Notion to markdown (external file, no caption)."""
    # Mock external file block
    block = Mock()
    block.type = "image"
    block.image = Mock()
    block.image.type = "external"
    block.image.external = Mock()
    block.image.external.url = "https://example.com/image.png"
    block.image.caption = []

    result = await ImageElement.notion_to_markdown(block)
    assert result == "[image](https://example.com/image.png)"


@pytest.mark.asyncio
async def test_notion_to_markdown_external_with_caption():
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

    result = await ImageElement.notion_to_markdown(block)
    assert result == "[image](https://example.com/photo.jpg)(caption:Beautiful sunset)"


@pytest.mark.asyncio
async def test_notion_to_markdown_notion_hosted():
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

    result = await ImageElement.notion_to_markdown(block)
    assert result == "[image](https://notion.s3.amazonaws.com/image123.png)"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.image = None
    assert await ImageElement.notion_to_markdown(paragraph_block) is None

    # No image content
    image_block = Mock()
    image_block.type = "image"
    image_block.image = None
    assert await ImageElement.notion_to_markdown(image_block) is None

    # Unsupported file type
    upload_block = Mock()
    upload_block.type = "image"
    upload_block.image = Mock()
    upload_block.image.type = "file_upload"
    upload_block.image.external = None
    upload_block.image.file = None
    assert await ImageElement.notion_to_markdown(upload_block) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("[image](https://example.com/pic.jpg)", True),
        (
            "[image](https://test.com/img.png)(caption:Caption)",
            True,
        ),  # Fixed: new caption syntax
        ("[image](http://site.org/photo.gif)", True),
        ("  [image](https://example.com/img.jpg)  ", True),  # With whitespace
        ("[img](https://example.com/pic.jpg)", False),  # Wrong prefix
        ("[image](not-a-url)", False),  # Invalid URL
        ("[image]()", False),  # Empty URL
        ("Regular text", False),
        ("", False),
    ],
)
async def test_markdown_patterns(markdown, should_match):
    """Test various markdown patterns."""
    result = await ImageElement.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None


@pytest.mark.asyncio
async def test_pattern_matching():
    """Test that the element can handle various patterns."""
    # Valid patterns should work
    assert (
        await ImageElement.markdown_to_notion("[image](https://example.com/pic.jpg)")
        is not None
    )
    assert (
        await ImageElement.markdown_to_notion(
            "[image](https://test.com/img.png)(caption:Caption)"
        )
        is not None
    )

    # Invalid patterns should not
    assert (
        await ImageElement.markdown_to_notion("[img](https://example.com/pic.jpg)")
        is None
    )
    assert await ImageElement.markdown_to_notion("[image](not-a-url)") is None
    assert await ImageElement.markdown_to_notion("[image]()") is None


@pytest.mark.asyncio
async def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "[image](https://example.com/image.jpg)",
        "[image](https://example.com/photo.png)(caption:Sunset)",
        "[image](http://site.org/diagram.gif)",
    ]

    for markdown in test_cases:
        # Convert to notion
        notion_result = await ImageElement.markdown_to_notion(markdown)
        assert notion_result is not None

        # Create proper Block mock for roundtrip
        notion_block = Mock()
        notion_block.type = "image"
        notion_block.image = notion_result.image

        # Convert back to markdown
        back_to_markdown = await ImageElement.notion_to_markdown(notion_block)
        assert back_to_markdown == markdown


@pytest.mark.asyncio
async def test_caption_with_special_characters():
    """Test captions with special characters."""
    markdown = (
        "[image](https://example.com/pic.jpg)(caption:Photo with ümlaut & emoji 🌅)"
    )
    result = await ImageElement.markdown_to_notion(markdown)

    assert result is not None
    image_block = result
    caption_text = image_block.image.caption[0].plain_text
    assert caption_text == "Photo with ümlaut & emoji 🌅"


@pytest.mark.asyncio
async def test_multiple_caption_parts():
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

    result = await ImageElement.notion_to_markdown(block)
    assert result == "[image](https://example.com/pic.jpg)(caption:Part 1 Part 2)"
