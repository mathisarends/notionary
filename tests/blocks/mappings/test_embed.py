from unittest.mock import Mock

import pytest

from notionary.blocks.mappings.embed import EmbedElement
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import CreateEmbedBlock, EmbedData, ExternalFile, FileUploadFile, NotionHostedFile


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid embed formats."""
    assert await EmbedElement.markdown_to_notion("[embed](https://example.com)")
    assert await EmbedElement.markdown_to_notion('[embed](https://youtube.com/watch?v=123 "Video")')
    assert await EmbedElement.markdown_to_notion("[embed](http://site.org/content)")
    assert await EmbedElement.markdown_to_notion("  [embed](https://example.com)  ")


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not await EmbedElement.markdown_to_notion("[image](https://example.com)")  # Wrong prefix
    assert not await EmbedElement.markdown_to_notion("[embed](not-a-url)")  # Invalid URL
    assert not await EmbedElement.markdown_to_notion("[embed]()")  # Empty URL
    assert not await EmbedElement.markdown_to_notion("[embed](ftp://example.com)")  # Non-http protocol
    assert await EmbedElement.markdown_to_notion("Regular text") is None
    assert await EmbedElement.markdown_to_notion("") is None


def test_match_notion():
    """Test recognition of Notion embed blocks."""
    # Valid embed block
    embed_block = Mock()
    embed_block.type = "embed"
    embed_block.embed = Mock()  # Not None
    assert EmbedElement.match_notion(embed_block)

    # Invalid blocks
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.embed = None
    assert not EmbedElement.match_notion(paragraph_block)

    # Embed type but embed is None
    empty_embed_block = Mock()
    empty_embed_block.type = "embed"
    empty_embed_block.embed = None
    assert not EmbedElement.match_notion(empty_embed_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_without_caption():
    """Test conversion from markdown to Notion without caption."""
    result = await EmbedElement.markdown_to_notion("[embed](https://youtube.com/watch?v=123)")

    assert result is not None
    assert isinstance(result, CreateEmbedBlock)
    assert result.type == "embed"
    assert isinstance(result.embed, EmbedData)
    assert result.embed.url == "https://youtube.com/watch?v=123"
    assert result.embed.caption == []


@pytest.mark.asyncio
async def test_markdown_to_notion_with_caption():
    """Test conversion from markdown to Notion with caption."""
    result = await EmbedElement.markdown_to_notion('[embed](https://example.com "My Video")')

    assert result is not None
    assert result.embed.url == "https://example.com"
    assert len(result.embed.caption) == 1
    assert result.embed.caption[0].plain_text == "My Video"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert await EmbedElement.markdown_to_notion("[image](https://example.com)") is None
    assert await EmbedElement.markdown_to_notion("[embed]()") is None
    assert await EmbedElement.markdown_to_notion("[embed](ftp://example.com)") is None
    assert await EmbedElement.markdown_to_notion("text") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_external_file():
    """Test conversion from Notion to markdown (ExternalFile)."""
    # Mock external file embed
    block = Mock()
    block.type = "embed"

    # Create mock ExternalFile
    external_file = Mock(spec=ExternalFile)
    external_file.url = "https://youtube.com/watch?v=abc123"
    external_file.caption = []

    block.embed = external_file

    result = await EmbedElement.notion_to_markdown(block)
    assert result == "[embed](https://youtube.com/watch?v=abc123)"


@pytest.mark.asyncio
async def test_notion_to_markdown_external_file_with_caption():
    """Test conversion with caption (ExternalFile)."""
    # Mock external file embed with caption
    block = Mock()
    block.type = "embed"

    external_file = Mock(spec=ExternalFile)
    external_file.url = "https://example.com/video"

    # Mock caption with real RichText
    caption_rt = RichText.from_plain_text("Cool Video")
    external_file.caption = [caption_rt]

    block.embed = external_file

    result = await EmbedElement.notion_to_markdown(block)
    assert result == '[embed](https://example.com/video "Cool Video")'


@pytest.mark.asyncio
async def test_notion_to_markdown_notion_hosted_file():
    """Test conversion from NotionHostedFile."""
    # Mock notion-hosted file
    block = Mock()
    block.type = "embed"

    notion_file = Mock(spec=NotionHostedFile)
    notion_file.url = "https://notion.s3.amazonaws.com/embed123"
    notion_file.caption = []

    block.embed = notion_file

    result = await EmbedElement.notion_to_markdown(block)
    assert result == "[embed](https://notion.s3.amazonaws.com/embed123)"


@pytest.mark.asyncio
async def test_notion_to_markdown_file_upload_unsupported():
    """Test that FileUploadFile is unsupported."""
    # Mock file upload (should be unsupported)
    block = Mock()
    block.type = "embed"

    upload_file = Mock(spec=FileUploadFile)
    upload_file.url = "some-upload-url"
    upload_file.caption = []

    block.embed = upload_file

    result = await EmbedElement.notion_to_markdown(block)
    assert result is None  # FileUploadFile is unsupported


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.embed = None
    assert await EmbedElement.notion_to_markdown(paragraph_block) is None

    # No embed content
    embed_block = Mock()
    embed_block.type = "embed"
    embed_block.embed = None
    assert await EmbedElement.notion_to_markdown(embed_block) is None

    # Unknown file object type
    unknown_block = Mock()
    unknown_block.type = "embed"
    unknown_block.embed = "unknown_type"  # Not a known FileObject
    assert await EmbedElement.notion_to_markdown(unknown_block) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("[embed](https://example.com)", True),
        ('[embed](https://youtube.com/watch?v=123 "Video")', True),
        ("[embed](http://site.org/content)", True),
        ("  [embed](https://example.com)  ", True),  # With whitespace
        ("[image](https://example.com)", False),  # Wrong prefix
        ("[embed](not-a-url)", False),  # Invalid URL
        ("[embed]()", False),  # Empty URL
        ("[embed](ftp://example.com)", False),  # Non-http protocol
        ("Regular text", False),
        ("", False),
    ],
)
async def test_markdown_patterns(markdown, should_match):
    """Test various markdown patterns."""
    result = await EmbedElement.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None


def test_pattern_matching():
    """Test the regex pattern directly."""
    pattern = EmbedElement.PATTERN

    # Valid patterns
    assert pattern.match("[embed](https://example.com)")
    assert pattern.match('[embed](https://test.com "Caption")')

    # Invalid patterns
    assert not pattern.match("[image](https://example.com)")
    assert not pattern.match("[embed](not-a-url)")
    assert not pattern.match("[embed]()")


@pytest.mark.asyncio
async def test_url_protocols():
    """Test different URL protocols."""
    valid_urls = [
        "[embed](https://example.com)",
        "[embed](http://example.com)",
        "[embed](https://youtube.com/watch?v=abc123)",
        "[embed](http://vimeo.com/123456789)",
    ]

    for url in valid_urls:
        assert await EmbedElement.markdown_to_notion(url) is not None
        result = await EmbedElement.markdown_to_notion(url)
        assert result is not None

    # Invalid protocols
    invalid_urls = [
        "[embed](ftp://example.com)",
        "[embed](file://local/file)",
        "[embed](mailto:test@example.com)",
    ]

    for url in invalid_urls:
        assert await EmbedElement.markdown_to_notion(url) is None


@pytest.mark.asyncio
async def test_roundtrip_conversion_external():
    """Test markdown -> notion -> markdown with ExternalFile."""
    test_cases = [
        "[embed](https://youtube.com/watch?v=123)",
        '[embed](https://example.com/video "Great Content")',
        "[embed](http://site.org/embed)",
    ]

    for original_markdown in test_cases:
        # Convert to notion
        notion_result = await EmbedElement.markdown_to_notion(original_markdown)
        assert notion_result is not None

        # Create mock ExternalFile block for notion_to_markdown
        block = Mock()
        block.type = "embed"

        external_file = Mock(spec=ExternalFile)
        external_file.url = notion_result.embed.url
        external_file.caption = notion_result.embed.caption

        block.embed = external_file

        # Convert back to markdown
        result_markdown = await EmbedElement.notion_to_markdown(block)
        assert result_markdown == original_markdown


@pytest.mark.asyncio
async def test_caption_with_special_characters():
    """Test captions with special characters."""
    markdown = '[embed](https://example.com "Caption with ümlaut & emoji 🎥")'
    result = await EmbedElement.markdown_to_notion(markdown)

    assert result is not None
    caption_text = result.embed.caption[0].plain_text
    assert caption_text == "Caption with ümlaut & emoji 🎥"


@pytest.mark.asyncio
async def test_multiple_caption_parts():
    """Test notion_to_markdown with multiple rich text objects in caption."""
    block = Mock()
    block.type = "embed"

    external_file = Mock(spec=ExternalFile)
    external_file.url = "https://example.com"

    # Multiple rich text objects in caption
    rt1 = RichText.from_plain_text("Part 1 ")
    rt2 = RichText.from_plain_text("Part 2")
    external_file.caption = [rt1, rt2]

    block.embed = external_file

    result = await EmbedElement.notion_to_markdown(block)
    assert result == '[embed](https://example.com "Part 1 Part 2")'


@pytest.mark.asyncio
async def test_different_embed_types():
    """Test various embed URL types."""
    embed_urls = [
        "https://youtube.com/watch?v=abc123",
        "https://vimeo.com/123456789",
        "https://codepen.io/user/pen/abcdef",
        "https://figma.com/file/abc/Design",
        "https://twitter.com/user/status/123",
        "https://docs.google.com/document/d/abc123",
    ]

    for url in embed_urls:
        markdown = f"[embed]({url})"
        assert await EmbedElement.markdown_to_notion(markdown) is not None
        result = await EmbedElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.embed.url == url
