from unittest.mock import Mock

import pytest

from notionary.blocks.mappings.video import VideoMapper
from notionary.blocks.schemas import CreateVideoBlock, VideoData


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid video formats."""
    assert await VideoMapper.markdown_to_notion("[video](https://example.com/video.mp4)")
    assert await VideoMapper.markdown_to_notion("[video](https://example.com/video.mp4)(caption:Caption)")
    assert await VideoMapper.markdown_to_notion("[video](https://youtu.be/dQw4w9WgXcQ)")
    assert await VideoMapper.markdown_to_notion("[video](https://youtube.com/watch?v=dQw4w9WgXcQ)")
    assert await VideoMapper.markdown_to_notion("  [video](https://example.com/video.mov)  ")


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid video formats."""
    assert await VideoMapper.markdown_to_notion("[video]") is None
    assert not await VideoMapper.markdown_to_notion("[video]()")
    # Note: With file upload support, "not-a-url" is treated as potential local file
    result = await VideoMapper.markdown_to_notion("[video](not-a-url)")
    assert result is not None  # Now works with file upload support

    # FTP URLs are now accepted as external URLs (validation happens at API level)
    result_ftp = await VideoMapper.markdown_to_notion("[video](ftp://example.com/video.mp4)")
    assert result_ftp is not None  # Now works with file upload support

    assert not await VideoMapper.markdown_to_notion("video(https://example.com/video.mp4)")  # Missing brackets
    assert not await VideoMapper.markdown_to_notion("[embed](https://example.com/video.mp4)")  # Wrong tag
    assert await VideoMapper.markdown_to_notion("") is None
    assert await VideoMapper.markdown_to_notion("Regular text") is None


def test_match_notion_valid():
    """Test recognition of valid Notion video blocks."""
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = Mock()

    assert VideoMapper.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.video = Mock()
    assert not VideoMapper.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = None
    assert not VideoMapper.match_notion(mock_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_basic():
    """Test conversion from markdown to Notion."""
    result = await VideoMapper.markdown_to_notion("[video](https://example.com/video.mp4)")

    assert result is not None
    assert isinstance(result, CreateVideoBlock)
    assert isinstance(result.video, VideoData)


@pytest.mark.asyncio
async def test_markdown_to_notion_with_caption():
    """Test conversion with caption."""
    result = await VideoMapper.markdown_to_notion("[video](https://example.com/video.mp4)(caption:Demo video)")

    assert result is not None
    assert isinstance(result, CreateVideoBlock)
    assert len(result.video.caption) > 0  # Should have caption


@pytest.mark.asyncio
async def test_markdown_to_notion_without_caption():
    """Test conversion without caption."""
    result = await VideoMapper.markdown_to_notion("[video](https://example.com/video.mp4)")

    assert result is not None
    video_block = result
    assert len(video_block.video.caption) == 0  # Should have no caption


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await VideoMapper.markdown_to_notion("[video]()") is None
    # Note: With file upload support, "not-a-url" is treated as potential local file
    result = await VideoMapper.markdown_to_notion("[video](not-a-url)")
    assert result is not None  # Now works with file upload support
    assert await VideoMapper.markdown_to_notion("Regular text") is None
    assert await VideoMapper.markdown_to_notion("") is None


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

    result = await VideoMapper.notion_to_markdown(mock_block)

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

    result = await VideoMapper.notion_to_markdown(mock_block)

    assert result is not None
    assert "https://example.com/uploaded.mp4" in result


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert await VideoMapper.notion_to_markdown(mock_block) is None

    mock_block.type = "video"
    mock_block.video = None
    assert await VideoMapper.notion_to_markdown(mock_block) is None


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
        result = VideoMapper._get_youtube_id(url)
        assert result == expected_id


def test_pattern_regex_directly():
    """Test the PATTERN regex directly."""
    pattern = VideoMapper.VIDEO_PATTERN

    # Valid patterns
    assert pattern.match("[video](https://example.com/video.mp4)")
    assert pattern.match("[video](https://example.com/video.mp4)(caption:Caption)")

    # Invalid patterns
    assert not pattern.match("[video]()")
    # Note: The regex itself matches any non-empty content inside parentheses
    # The "not-a-url" case matches the pattern but validation happens later
    assert pattern.match("[video](not-a-url)")  # Pattern matches, validation is separate
    assert not pattern.match("video(https://example.com)")


def test_youtube_patterns():
    """Test YouTube pattern matching."""
    youtube_patterns = VideoMapper.YOUTUBE_PATTERNS

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

        assert await VideoMapper.markdown_to_notion(markdown) is not None
        result = await VideoMapper.markdown_to_notion(markdown)
        assert result is not None


@pytest.mark.asyncio
async def test_whitespace_handling():
    """Test handling of whitespace."""
    assert await VideoMapper.markdown_to_notion("  [video](https://example.com/video.mp4)  ")

    result = await VideoMapper.markdown_to_notion("  [video](https://example.com/video.mp4)  ")
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
        assert await VideoMapper.markdown_to_notion(markdown) is not None

    # With file upload support, FTP is now accepted as external URL
    result_ftp = await VideoMapper.markdown_to_notion("[video](ftp://example.com/video.mp4)")
    assert result_ftp is not None  # Element accepts FTP, validation happens at API level

    # Note: file:// URLs cause issues because they're treated as local paths that don't exist
    # This is expected behavior - if you specify a local file, it should exist
