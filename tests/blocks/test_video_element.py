"""
Minimal tests for VideoElement.
Tests core functionality for video blocks with [video](url) syntax.
"""

from unittest.mock import Mock
from notionary.blocks.video.video_element import VideoElement
from notionary.blocks.video.video_element_models import CreateVideoBlock
from notionary.blocks.file.file_element_models import FileBlock
from notionary.blocks.paragraph.paragraph_models import CreateParagraphBlock


def test_match_markdown_valid():
    """Test recognition of valid video formats."""
    assert VideoElement.markdown_to_notion("[video](https://example.com/video.mp4)")
    assert VideoElement.markdown_to_notion(
        '[video](https://example.com/video.mp4 "Caption")'
    )
    assert VideoElement.markdown_to_notion("[video](https://youtu.be/dQw4w9WgXcQ)")
    assert VideoElement.markdown_to_notion(
        "[video](https://youtube.com/watch?v=dQw4w9WgXcQ)"
    )
    assert VideoElement.markdown_to_notion("  [video](https://example.com/video.mov)  ")


def test_match_markdown_invalid():
    """Test rejection of invalid video formats."""
    assert VideoElement.markdown_to_notion("[video]") is None
    assert not VideoElement.markdown_to_notion("[video]()")
    assert not VideoElement.markdown_to_notion("[video](not-a-url)")
    assert not VideoElement.markdown_to_notion(
        "[video](ftp://example.com/video.mp4)"
    )  # Only http/https
    assert not VideoElement.markdown_to_notion(
        "video(https://example.com/video.mp4)"
    )  # Missing brackets
    assert not VideoElement.markdown_to_notion(
        "[embed](https://example.com/video.mp4)"
    )  # Wrong tag
    assert VideoElement.markdown_to_notion("") is None
    assert VideoElement.markdown_to_notion("Regular text") is None


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


def test_markdown_to_notion_basic():
    """Test conversion from markdown to Notion."""
    result = VideoElement.markdown_to_notion("[video](https://example.com/video.mp4)")

    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2  # Video block + empty paragraph

    # First block should be video
    video_block = result[0]
    assert isinstance(video_block, CreateVideoBlock)
    assert isinstance(video_block.video, FileBlock)

    # Second block should be empty paragraph
    para_block = result[1]
    assert isinstance(para_block, CreateParagraphBlock)


def test_markdown_to_notion_with_caption():
    """Test conversion with caption."""
    result = VideoElement.markdown_to_notion(
        '[video](https://example.com/video.mp4 "Demo video")'
    )

    assert result is not None
    assert len(result) == 2

    video_block = result[0]
    assert len(video_block.video.caption) > 0  # Should have caption


def test_markdown_to_notion_without_caption():
    """Test conversion without caption."""
    result = VideoElement.markdown_to_notion("[video](https://example.com/video.mp4)")

    assert result is not None
    video_block = result[0]
    assert len(video_block.video.caption) == 0  # Should have no caption


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert VideoElement.markdown_to_notion("[video]()") is None
    assert VideoElement.markdown_to_notion("[video](not-a-url)") is None
    assert VideoElement.markdown_to_notion("Regular text") is None
    assert VideoElement.markdown_to_notion("") is None


def test_notion_to_markdown_external():
    """Test conversion from Notion to markdown (external URL)."""
    # Create mock video block
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = Mock()
    mock_block.video.type = "external"
    mock_block.video.external = Mock()
    mock_block.video.external.url = "https://example.com/video.mp4"
    mock_block.video.caption = []

    result = VideoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result == "[video](https://example.com/video.mp4)"


def test_notion_to_markdown_with_caption():
    """Test conversion with caption."""
    # Create mock rich text for caption
    mock_caption = Mock()
    mock_caption.plain_text = "Demo video"
    mock_caption.model_dump.return_value = {"text": {"content": "Demo video"}}

    # Create mock video block
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = Mock()
    mock_block.video.type = "external"
    mock_block.video.external = Mock()
    mock_block.video.external.url = "https://example.com/video.mp4"
    mock_block.video.caption = [mock_caption]

    result = VideoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert "Demo video" in result
    assert result.startswith("[video](")
    assert '"Demo video")' in result


def test_notion_to_markdown_file_type():
    """Test conversion with file type (not external)."""
    mock_block = Mock()
    mock_block.type = "video"
    mock_block.video = Mock()
    mock_block.video.type = "file"
    mock_block.video.file = Mock()
    mock_block.video.file.url = "https://example.com/uploaded.mp4"
    mock_block.video.caption = []
    mock_block.video.external = None

    result = VideoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert "https://example.com/uploaded.mp4" in result


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert VideoElement.notion_to_markdown(mock_block) is None

    mock_block.type = "video"
    mock_block.video = None
    assert VideoElement.notion_to_markdown(mock_block) is None


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
    pattern = VideoElement.PATTERN

    # Valid patterns
    assert pattern.match("[video](https://example.com/video.mp4)")
    assert pattern.match('[video](https://example.com/video.mp4 "Caption")')

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


def test_video_file_extensions():
    """Test various video file extensions."""
    extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"]

    for ext in extensions:
        url = f"https://example.com/video{ext}"
        markdown = f"[video]({url})"

        assert VideoElement.markdown_to_notion(markdown) is not None
        result = VideoElement.markdown_to_notion(markdown)
        assert result is not None


def test_whitespace_handling():
    """Test handling of whitespace."""
    assert VideoElement.markdown_to_notion("  [video](https://example.com/video.mp4)  ")

    result = VideoElement.markdown_to_notion(
        "  [video](https://example.com/video.mp4)  "
    )
    assert result is not None


def test_url_protocols():
    """Test different URL protocols."""
    # Valid protocols
    valid_urls = [
        "https://example.com/video.mp4",
        "http://example.com/video.mp4",
    ]

    for url in valid_urls:
        markdown = f"[video]({url})"
        assert VideoElement.markdown_to_notion(markdown) is not None

    # Invalid protocols should not match the pattern
    invalid_urls = [
        "ftp://example.com/video.mp4",
        "file:///local/video.mp4",
    ]

    for url in invalid_urls:
        markdown = f"[video]({url})"
        assert VideoElement.markdown_to_notion(markdown) is None
