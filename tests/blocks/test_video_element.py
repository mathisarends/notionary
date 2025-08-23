"""
Minimal tests for VideoElement.
Tests core functionality for video blocks with [video](url) syntax.
"""

from unittest.mock import Mock

import pytest

from notionary.blocks.file.file_element_models import FileBlock
from notionary.blocks.paragraph.paragraph_models import CreateParagraphBlock
from notionary.blocks.video.video_element import VideoElement
from notionary.blocks.video.video_element_models import CreateVideoBlock


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid video formats."""
    assert await VideoElement.markdown_to_notion(
        "[video](https://example.com/video.mp4)"
    )
    assert await VideoElement.markdown_to_notion(
        "[video](https://example.com/video.mp4)(caption:Caption)"
    )
    assert await VideoElement.markdown_to_notion(
        "[video](https://youtu.be/dQw4w9WgXcQ)"
    )
    assert await VideoElement.markdown_to_notion(
        "[video](https://youtube.com/watch?v=dQw4w9WgXcQ)"
    )
    assert await VideoElement.markdown_to_notion(
        "  [video](https://example.com/video.mov)  "
    )


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid video formats."""
    assert await VideoElement.markdown_to_notion("[video]") is None
    assert not await VideoElement.markdown_to_notion("[video]()")
    assert not await VideoElement.markdown_to_notion("[video](not-a-url)")
    assert not await VideoElement.markdown_to_notion(
        "[video](ftp://example.com/video.mp4)"
    )  # Only http/https
    assert not await VideoElement.markdown_to_notion(
        "video(https://example.com/video.mp4)"
    )  # Missing brackets
    assert not await VideoElement.markdown_to_notion(
        "[embed](https://example.com/video.mp4)"
    )  # Wrong tag
    assert await VideoElement.markdown_to_notion("") is None
    assert await VideoElement.markdown_to_notion("Regular text") is None


def test_match_notion_valid():
    """Test recognition of valid Notion video blocks."""
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = Mock()

    assert VideoElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.video = Mock()
    assert not VideoElement.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = None
    assert not VideoElement.match_notion(mock_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_basic():
    """Test conversion from markdown to Notion."""
    result = await VideoElement.markdown_to_notion(
        "[video](https://example.com/video.mp4)"
    )

    assert result is not None
    assert isinstance(result, CreateVideoBlock)
    assert isinstance(result.video, FileBlock)


@pytest.mark.asyncio
async def test_markdown_to_notion_with_caption():
    """Test conversion with caption."""
    result = await VideoElement.markdown_to_notion(
        "[video](https://example.com/video.mp4)(caption:Demo video)"
    )

    assert result is not None
    assert isinstance(result, CreateVideoBlock)
    assert len(result.video.caption) > 0  # Should have caption


@pytest.mark.asyncio
async def test_markdown_to_notion_without_caption():
    """Test conversion without caption."""
    result = await VideoElement.markdown_to_notion(
        "[video](https://example.com/video.mp4)"
    )

    assert result is not None
    video_block = result
    assert len(video_block.video.caption) == 0  # Should have no caption


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await VideoElement.markdown_to_notion("[video]()") is None
    assert await VideoElement.markdown_to_notion("[video](not-a-url)") is None
    assert await VideoElement.markdown_to_notion("Regular text") is None
    assert await VideoElement.markdown_to_notion("") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_external():
    """Test conversion from Notion to markdown (external URL)."""
    # Create mock video block
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = Mock()
    mock_block.video.type = "external"
    mock_block.video.external = Mock()
    mock_block.video.external.url = "https://example.com/video.mp4"
    mock_block.video.caption = []

    result = await VideoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result == "[video](https://example.com/video.mp4)"


@pytest.mark.asyncio
async def test_notion_to_markdown_file_type():
    """Test conversion with file type (not external)."""
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = Mock()
    mock_block.video.type = "file"
    mock_block.video.file = Mock()
    mock_block.video.file.url = "https://example.com/uploaded.mp4"
    mock_block.video.caption = []
    mock_block.video.external = None

    result = await VideoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert "https://example.com/uploaded.mp4" in result


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert await VideoElement.notion_to_markdown(mock_block) is None

    mock_block.type = "video"
    mock_block.video = None
    assert await VideoElement.notion_to_markdown(mock_block) is None


def test_get_youtube_id():
    """Test YouTube ID extraction."""
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("youtube.com/watch?v=abc123DEF45", "abc123DEF45"),
        ("youtu.be/xyz789GHI01", "xyz789GHI01"),
        ("https://example.com/video.mp4", None),  # Not YouTube
        ("not-a-url", None),
    ]

    for url, expected_id in test_cases:
        result = VideoElement._get_youtube_id(url)
        assert result == expected_id


def test_pattern_regex_directly():
    """Test the PATTERN regex directly."""
    pattern = VideoElement.VIDEO_PATTERN

    # Valid patterns
    assert pattern.match("[video](https://example.com/video.mp4)")
    assert pattern.match("[video](https://example.com/video.mp4)(caption:Caption)")

    # Invalid patterns
    assert not pattern.match("[video]()")
    assert not pattern.match("[video](not-a-url)")
    assert not pattern.match("video(https://example.com)")


def test_youtube_patterns():
    """Test YouTube pattern matching."""
    youtube_patterns = VideoElement.YOUTUBE_PATTERNS

    youtube_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "youtube.com/watch?v=abc123DEF45",
        "youtu.be/xyz789GHI01",
    ]

    non_youtube_urls = [
        "https://vimeo.com/123456789",
        "https://example.com/video.mp4",
        "not-a-url",
    ]

    for url in youtube_urls:
        found_match = any(pattern.match(url) for pattern in youtube_patterns)
        assert found_match, f"Should match YouTube URL: {url}"

    for url in non_youtube_urls:
        found_match = any(pattern.match(url) for pattern in youtube_patterns)
        assert not found_match, f"Should not match non-YouTube URL: {url}"


@pytest.mark.asyncio
async def test_video_file_extensions():
    """Test various video file extensions."""
    extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"]

    for ext in extensions:
        url = f"https://example.com/video{ext}"
        markdown = f"[video]({url})"

        assert await VideoElement.markdown_to_notion(markdown) is not None
        result = await VideoElement.markdown_to_notion(markdown)
        assert result is not None


@pytest.mark.asyncio
async def test_whitespace_handling():
    """Test handling of whitespace."""
    assert await VideoElement.markdown_to_notion(
        "  [video](https://example.com/video.mp4)  "
    )

    result = await VideoElement.markdown_to_notion(
        "  [video](https://example.com/video.mp4)  "
    )
    assert result is not None


@pytest.mark.asyncio
async def test_url_protocols():
    """Test different URL protocols."""
    # Valid protocols
    valid_urls = [
        "https://example.com/video.mp4",
        "http://example.com/video.mp4",
    ]

    for url in valid_urls:
        markdown = f"[video]({url})"
        assert await VideoElement.markdown_to_notion(markdown) is not None

    # Invalid protocols should not match the pattern
    invalid_urls = [
        "ftp://example.com/video.mp4",
        "file:///local/video.mp4",
    ]

    for url in invalid_urls:
        markdown = f"[video]({url})"
        assert await VideoElement.markdown_to_notion(markdown) is None
