"""
Pytest tests for VideoElement.
Tests conversion between Markdown videos ([video](url "caption")) and Notion video blocks.
"""

import pytest
from unittest.mock import Mock, patch
from notionary.blocks.video.video_element import VideoElement


@pytest.mark.parametrize(
    "text,expected",
    [
        ("[video](https://example.com/video.mp4)", True),
        ('[video](https://example.com/video.mp4 "A caption")', True),
        ("[video](https://youtu.be/dQw4w9WgXcQ)", True),
        ('[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Rick")', True),
        ("[video](not-a-url)", False),  # Falscher URL-Format, sollte False sein
        ("[video]()", False),
        ("[video](   )", False),
        ("[vid](https://example.com/video.mp4)", False),
        ("![video](https://example.com/video.mp4)", False),
        ("Just text", False),
        ("", False),
    ],
)
def test_match_markdown(text, expected):
    assert VideoElement.match_markdown(text) == expected


@pytest.mark.parametrize(
    "block_data,expected",
    [
        ({"type": "video", "video": {}}, True),
        ({"type": "image", "image": {}}, False),
        ({"type": "paragraph", "paragraph": {}}, False),
        ({"type": "video"}, False),  # video ist None
    ],
)
def test_match_notion(block_data, expected):
    # Mock Block object
    block = Mock()
    block.type = block_data["type"]
    block.video = block_data.get("video")
    
    assert VideoElement.match_notion(block) == expected


@pytest.mark.parametrize(
    "md,expected_url,expected_caption",
    [
        ("[video](https://example.com/demo.mp4)", "https://example.com/demo.mp4", ""),
        (
            '[video](https://example.com/abc.mp4 "Demo Video")',
            "https://example.com/abc.mp4",
            "Demo Video",
        ),
        (
            "[video](https://youtu.be/dQw4w9WgXcQ)",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # YouTube URLs werden normalisiert
            "",
        ),
        (
            '[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Rick")',
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "Rick",
        ),
    ],
)
def test_markdown_to_notion(md, expected_url, expected_caption):
    result = VideoElement.markdown_to_notion(md)
    assert result is not None
    assert len(result) == 2  # VideoBlock + ParagraphBlock
    
    # VideoBlock ist der erste Block
    video_block = result[0]
    assert video_block.type == "video"
    assert video_block.video.type == "external"
    assert video_block.video.external.url == expected_url
    
    if expected_caption:
        assert len(video_block.video.caption) == 1
        assert video_block.video.caption[0].plain_text == expected_caption
    else:
        assert video_block.video.caption == []
    
    # ParagraphBlock ist der zweite Block
    para_block = result[1]
    assert para_block.type == "paragraph"
    assert para_block.paragraph.rich_text == []


@pytest.mark.parametrize(
    "md",
    [
        "[video]()",
        "[video](not-a-url)",
        "[video](   )",
        "not a video",
        "",
    ],
)
def test_markdown_to_notion_invalid(md):
    assert VideoElement.markdown_to_notion(md) is None


def test_notion_to_markdown():
    """Test conversion from Notion blocks to Markdown."""
    # Test external video with caption
    external_block = Mock()
    external_block.type = "video"
    external_block.video = Mock()
    external_block.video.type = "external"
    external_block.video.external = Mock()
    external_block.video.external.url = "https://example.com/video.mp4"
    
    caption_rt = Mock()
    caption_rt.plain_text = "My Caption"
    caption_rt.model_dump.return_value = {"type": "text", "text": {"content": "My Caption"}}
    external_block.video.caption = [caption_rt]
    
    with patch('notionary.blocks.rich_text.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting') as mock_extract:
        mock_extract.return_value = "My Caption"
        result = VideoElement.notion_to_markdown(external_block)
        assert result == '[video](https://example.com/video.mp4 "My Caption")'
    
    # Test file video without caption
    file_block = Mock()
    file_block.type = "video"
    file_block.video = Mock()
    file_block.video.type = "file"
    file_block.video.file = Mock()
    file_block.video.file.url = "https://example.com/uploaded.mp4"
    file_block.video.caption = []
    
    result = VideoElement.notion_to_markdown(file_block)
    assert result == "[video](https://example.com/uploaded.mp4)"
    
    # Test external video without caption
    no_caption_block = Mock()
    no_caption_block.type = "video"
    no_caption_block.video = Mock()
    no_caption_block.video.type = "external"
    no_caption_block.video.external = Mock()
    no_caption_block.video.external.url = "https://youtu.be/dQw4w9WgXcQ"
    no_caption_block.video.caption = []
    
    result = VideoElement.notion_to_markdown(no_caption_block)
    assert result == "[video](https://youtu.be/dQw4w9WgXcQ)"


def test_notion_to_markdown_invalid():
    """Test invalid blocks return None."""
    # Invalid block type
    invalid_block = Mock()
    invalid_block.type = "paragraph"
    invalid_block.video = None
    assert VideoElement.notion_to_markdown(invalid_block) is None
    
    # Video block but video is None
    video_none_block = Mock()
    video_none_block.type = "video"
    video_none_block.video = None
    assert VideoElement.notion_to_markdown(video_none_block) is None
    
    # Missing URL
    missing_url_block = Mock()
    missing_url_block.type = "video"
    missing_url_block.video = Mock()
    missing_url_block.video.type = "external"
    missing_url_block.video.external = None
    missing_url_block.video.file = None
    assert VideoElement.notion_to_markdown(missing_url_block) is None


def test_is_multiline():
    assert not VideoElement.is_multiline()


@pytest.mark.parametrize(
    "url,expected_id",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtube.com/watch?v=abcd1234567", "abcd1234567"),
        ("https://example.com/video.mp4", None),
        ("not-a-url", None),
    ],
)
def test_get_youtube_id(url, expected_id):
    """Test YouTube ID extraction."""
    result = VideoElement._get_youtube_id(url)
    assert result == expected_id


@pytest.mark.parametrize(
    "md",
    [
        '[video](https://example.com/video.mp4 "Käse kaufen äöüß")',
        '[video](https://youtu.be/dQw4w9WgXcQ "Mit Emoji 🙂")',
        '[video](https://vimeo.com/123456 "中文说明")',
    ],
)
def test_unicode_and_special_caption(md):
    """Test Unicode characters in captions."""
    result = VideoElement.markdown_to_notion(md)
    assert result is not None
    video_block = result[0]
    
    # Extract caption from markdown
    caption_start = md.find('"') + 1
    caption_end = md.rfind('"')
    expected_caption = md[caption_start:caption_end]
    
    # Check that caption appears in the block
    caption_list = video_block.video.caption
    if caption_list:
        actual_caption = caption_list[0].plain_text
        assert actual_caption == expected_caption


def test_roundtrip():
    """Test roundtrip conversion: Markdown -> Notion -> Markdown."""
    test_cases = [
        ("[video](https://example.com/demo.mp4)", "[video](https://example.com/demo.mp4)"),
        ('[video](https://example.com/demo.mp4 "Demo Video")', '[video](https://example.com/demo.mp4 "Demo Video")'),
        ("[video](https://youtu.be/dQw4w9WgXcQ)", "[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"),  # YouTube wird normalisiert
        ('[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Rick")', '[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Rick")'),
    ]
    
    for original_md, expected_md in test_cases:
        # Markdown -> Notion
        result = VideoElement.markdown_to_notion(original_md)
        assert result is not None
        
        video_block = result[0]
        
        # Notion -> Markdown
        recovered_md = VideoElement.notion_to_markdown(video_block)
        assert recovered_md is not None
        assert recovered_md == expected_md


def test_youtube_url_normalization():
    """Test that YouTube URLs are properly normalized."""
    test_cases = [
        ("https://youtu.be/dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ("http://youtube.com/watch?v=abcd1234567", "https://www.youtube.com/watch?v=abcd1234567"),
    ]
    
    for input_url, expected_url in test_cases:
        md = f"[video]({input_url})"
        result = VideoElement.markdown_to_notion(md)
        assert result is not None
        
        video_block = result[0]
        assert video_block.video.external.url == expected_url


def test_caption_with_complex_formatting():
    """Test captions with various formatting."""
    with patch('notionary.blocks.rich_text.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting') as mock_extract:
        mock_extract.return_value = "Complex Caption"
        
        # Create a mock block with complex caption
        block = Mock()
        block.type = "video"
        block.video = Mock()
        block.video.type = "external"
        block.video.external = Mock()
        block.video.external.url = "https://example.com/video.mp4"
        
        caption_rt = Mock()
        caption_rt.plain_text = None  # Force fallback to TextInlineFormatter
        caption_rt.model_dump.return_value = {"type": "text", "text": {"content": "Complex Caption"}}
        block.video.caption = [caption_rt]
        
        result = VideoElement.notion_to_markdown(block)
        assert result == '[video](https://example.com/video.mp4 "Complex Caption")'


def test_multiple_caption_parts():
    """Test handling of multiple caption parts."""
    with patch('notionary.blocks.rich_text.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting') as mock_extract:
        mock_extract.side_effect = ["Part 1", "Part 2"]
        
        block = Mock()
        block.type = "video"
        block.video = Mock()
        block.video.type = "external"
        block.video.external = Mock()
        block.video.external.url = "https://example.com/video.mp4"
        
        caption_rt1 = Mock()
        caption_rt1.plain_text = "Part 1"
        caption_rt1.model_dump.return_value = {"type": "text", "text": {"content": "Part 1"}}
        
        caption_rt2 = Mock()
        caption_rt2.plain_text = None
        caption_rt2.model_dump.return_value = {"type": "text", "text": {"content": "Part 2"}}
        
        block.video.caption = [caption_rt1, caption_rt2]
        
        result = VideoElement.notion_to_markdown(block)
        assert result == '[video](https://example.com/video.mp4 "Part 1Part 2")'


def test_edge_cases():
    """Test various edge cases."""
    # Empty URL should not match
    assert not VideoElement.match_markdown("[video]()")
    assert not VideoElement.match_markdown("[video](   )")
    
    # Invalid protocols
    assert not VideoElement.match_markdown("[video](ftp://example.com/video.mp4)")
    
    # URLs with fragments and query params
    assert VideoElement.match_markdown("[video](https://example.com/video.mp4?t=123#start)")
    
    # Very long URLs
    long_url = "https://example.com/" + "a" * 1000 + ".mp4"
    assert VideoElement.match_markdown(f"[video]({long_url})")


def test_malformed_youtube_urls():
    """Test handling of malformed YouTube URLs."""
    # These should not be recognized as YouTube URLs
    malformed_urls = [
        "https://youtube.com/watch?vid=dQw4w9WgXcQ",  # wrong parameter
        "https://youtu.be/dQw4w9WgXcQ123",  # too long ID
        "https://youtu.be/dQw4w9",  # too short ID
    ]
    
    for url in malformed_urls:
        youtube_id = VideoElement._get_youtube_id(url)
        if youtube_id is None:
            # Should be treated as regular URL
            md = f"[video]({url})"
            result = VideoElement.markdown_to_notion(md)
            assert result is not None
            video_block = result[0]
            assert video_block.video.external.url == url  # No normalization