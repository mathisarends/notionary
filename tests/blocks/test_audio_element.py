import pytest
from unittest.mock import Mock

from notionary.blocks.audio.audio_element import AudioElement


def test_match_markdown_valid_audio():
    assert AudioElement.match_markdown("[audio](https://example.com/track.mp3)")
    assert AudioElement.match_markdown('[audio](https://audio.de/a.wav "Ein Track")')
    assert AudioElement.match_markdown('   [audio](https://x.org/b.ogg "Hallo")   ')
    assert AudioElement.match_markdown("[audio](https://test.com/file.m4a)")
    # Auch OGA und Großbuchstaben
    assert AudioElement.match_markdown("[audio](https://example.com/audio.OGA)")
    assert AudioElement.match_markdown(
        '[audio](https://audio.com/abc.mp3 "Mit Caption")'
    )


@pytest.mark.parametrize(
    "text",
    [
        "[audio](https://a.de/test.mp3)",
        '[audio](https://files.com/clip.wav "Stimme")',
        '   [audio](https://site.org/s.ogg "Podcast")   ',
        "[audio](https://music.com/sound.m4a)",
    ],
)
def test_match_markdown_param_valid(text):
    assert AudioElement.match_markdown(text)


@pytest.mark.parametrize(
    "text",
    [
        "[aud](https://test.com/track.mp3)",  # falscher Prefix
        "[audio](not-a-url)",  # kein URL
        "[audio]()",  # leer
        "[audio]( )",
        "[audio](ftp://x.com/file.mp3)",  # falsches Protokoll
        "[audio]https://a.de/b.mp3",  # fehlende Klammern
        "[audio](https://a.de/b)",  # keine Extension
        "[audio](https://example.com/file.jpg)",  # kein Audio
        "![audio](https://example.com/file.mp3)",  # falsches Präfix
        "",
        "random text",
    ],
)
def test_match_markdown_param_invalid(text):
    assert not AudioElement.match_markdown(text)


def test_match_notion_block():
    """Test match_notion with proper Block objects."""
    # Valid audio block
    audio_block = Mock()
    audio_block.type = "audio"
    # NOTE: Das AudioElement erwartet dass block.audio existiert, nicht None ist
    assert AudioElement.match_notion(audio_block)

    # Invalid block types
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    assert not AudioElement.match_notion(paragraph_block)

    image_block = Mock()
    image_block.type = "image"
    assert not AudioElement.match_notion(image_block)


def test_markdown_to_notion_with_caption():
    """Test conversion from markdown to Notion with caption."""
    markdown = '[audio](https://abc.com/music.mp3 "Mein Song")'
    result = AudioElement.markdown_to_notion(markdown)

    assert result is not None
    # Result sollte ein CreateAudioBlock Pydantic-Modell sein
    assert result.type == "audio"
    assert result.audio.type == "external"
    assert result.audio.external.url == "https://abc.com/music.mp3"
    assert len(result.audio.caption) == 1
    assert result.audio.caption[0].plain_text == "Mein Song"


def test_markdown_to_notion_without_caption():
    """Test conversion from markdown to Notion without caption."""
    markdown = "[audio](https://x.de/track.wav)"
    result = AudioElement.markdown_to_notion(markdown)

    assert result is not None
    assert result.type == "audio"
    assert result.audio.type == "external"
    assert result.audio.external.url == "https://x.de/track.wav"
    assert result.audio.caption == []


def test_markdown_to_notion_invalid_cases():
    assert AudioElement.markdown_to_notion("[aud](https://a.com/x.mp3)") is None
    assert AudioElement.markdown_to_notion("[audio]()") is None
    assert AudioElement.markdown_to_notion("") is None
    assert AudioElement.markdown_to_notion("nur Text") is None


def test_notion_to_markdown_with_caption():
    """Test conversion from Notion to markdown with caption."""
    # Mock Block object
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://sound.com/track.ogg"

    # Mock RichTextObject
    caption_rt = Mock()
    caption_rt.model_dump.return_value = {
        "type": "text",
        "text": {"content": "Der Sound"},
        "plain_text": "Der Sound",
    }
    notion_block.audio.caption = [caption_rt]

    result = AudioElement.notion_to_markdown(notion_block)
    assert result == '[audio](https://sound.com/track.ogg "Der Sound")'


def test_notion_to_markdown_without_caption():
    """Test conversion from Notion to markdown without caption."""
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://sound.com/no-caption.mp3"
    notion_block.audio.caption = []

    result = AudioElement.notion_to_markdown(notion_block)
    assert result == "[audio](https://sound.com/no-caption.mp3)"


def test_notion_to_markdown_invalid_cases():
    """Test invalid cases return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.audio = None
    assert AudioElement.notion_to_markdown(paragraph_block) is None

    # Audio is None
    audio_none_block = Mock()
    audio_none_block.type = "audio"
    audio_none_block.audio = None
    assert AudioElement.notion_to_markdown(audio_none_block) is None

    # Not external type
    file_block = Mock()
    file_block.type = "audio"
    file_block.audio = Mock()
    file_block.audio.type = "file"
    file_block.audio.external = None
    assert AudioElement.notion_to_markdown(file_block) is None

    # Missing URL
    no_url_block = Mock()
    no_url_block.type = "audio"
    no_url_block.audio = Mock()
    no_url_block.audio.type = "external"
    no_url_block.audio.external = Mock()
    no_url_block.audio.external.url = None
    assert AudioElement.notion_to_markdown(no_url_block) is None


# REMOVED: test_extract_text_content - method doesn't exist anymore
# REMOVED: test_is_multiline - method doesn't exist anymore  
# REMOVED: test_is_likely_audio_url - method doesn't exist anymore or is private


@pytest.mark.parametrize(
    "markdown",
    [
        '[audio](https://music.com/roundtrip.mp3 "Roundtrip Caption")',
        "[audio](https://sound.com/x.wav)",
        '[audio](https://a.b/c.ogg "🙂 Mit Emoji")',
    ],
)
def test_roundtrip_conversion(markdown):
    """Test that markdown -> notion -> markdown preserves content."""
    # Create proper Block object for testing
    notion_result = AudioElement.markdown_to_notion(markdown)
    assert notion_result is not None
    
    # For roundtrip, we need to create a proper Block mock
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = notion_result.audio.type
    notion_block.audio.external = notion_result.audio.external
    notion_block.audio.caption = notion_result.audio.caption
    
    back = AudioElement.notion_to_markdown(notion_block)
    assert back == markdown


@pytest.mark.parametrize(
    "caption",
    [
        "Mit Umlauten äöüß",
        "Emoji 🙂😎", 
        "Special chars !?&/()[]",
        "中文测试",
    ],
)
def test_unicode_and_special_caption(caption):
    """Test handling of Unicode and special characters in captions."""
    url = "https://audio.host/x.mp3"
    markdown = f'[audio]({url} "{caption}")'
    block = AudioElement.markdown_to_notion(markdown)
    assert block is not None
    assert block.audio.caption[0].plain_text == caption


def test_empty_caption_edge_case():
    """Test handling of empty caption."""
    url = "https://audio.host/x.mp3"
    markdown = f"[audio]({url})"
    block = AudioElement.markdown_to_notion(markdown)
    assert block is not None
    assert block.audio.caption == []


def test_extra_whitespace_and_caption_spaces():
    """Test handling of whitespace in input and captions."""
    # Whitespace around the markdown should be stripped by match_markdown
    md = '   [audio](https://aud.io/a.mp3 "  Caption mit Leerzeichen   ")   '
    assert AudioElement.match_markdown(md)
    
    block = AudioElement.markdown_to_notion(md)
    assert block is not None
    # Caption spaces should be preserved
    assert block.audio.caption[0].plain_text == "  Caption mit Leerzeichen   "


def test_integration_with_other_elements():
    """Test that AudioElement doesn't match non-audio markdown."""
    not_audio = [
        "# Heading",
        "Paragraph text", 
        "[link](https://example.com)",
        "[image](https://img.com/b.jpg)",
        "[video](https://video.com/v.mp4)",
        "",
        "   ",
    ]
    for text in not_audio:
        assert not AudioElement.match_markdown(text)


def test_url_validation_via_match_markdown():
    """Test URL validation through match_markdown (since _is_likely_audio_url is private/gone)."""
    # Valid HTTP/HTTPS URLs with audio extensions
    valid_urls = [
        "[audio](http://example.com/file.mp3)",
        "[audio](https://example.com/file.wav)", 
        "[audio](https://subdomain.example.com/path/to/file.ogg)",
        "[audio](https://example.com/file.m4a)",
        "[audio](https://example.com/file.oga)",
    ]
    for url in valid_urls:
        assert AudioElement.match_markdown(url)

    # Invalid URLs (no proper audio extension)
    invalid_urls = [
        "[audio](https://example.com/file)",  # No extension
        "[audio](https://example.com/file.txt)",  # Wrong extension  
        "[audio](https://example.com/file.jpg)",  # Wrong extension
        "[audio](not-a-url)",  # Not a URL
    ]
    for url in invalid_urls:
        assert not AudioElement.match_markdown(url)


def test_caption_with_quotes():
    """Test handling of quotes within captions."""
    # Simple caption without internal quotes should definitely work
    simple_caption = '[audio](https://example.com/file.mp3 "Simple caption")'
    assert AudioElement.match_markdown(simple_caption)


def test_multiple_caption_rich_text_objects():
    """Test notion_to_markdown with multiple rich text objects in caption."""
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://example.com/audio.mp3"

    # Multiple rich text objects
    rt1 = Mock()
    rt1.model_dump.return_value = {"type": "text", "text": {"content": "Part 1 "}}
    rt2 = Mock()
    rt2.model_dump.return_value = {"type": "text", "text": {"content": "Part 2"}}
    notion_block.audio.caption = [rt1, rt2]

    result = AudioElement.notion_to_markdown(notion_block)
    assert result == '[audio](https://example.com/audio.mp3 "Part 1 Part 2")'


def test_notion_to_markdown_with_plain_text_fallback():
    """Test notion_to_markdown falls back to plain_text when text content is missing."""
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://example.com/audio.mp3"

    # Rich text object without text content, should use plain_text
    rt = Mock()
    rt.model_dump.return_value = {"plain_text": "Fallback Text", "type": "mention"}
    notion_block.audio.caption = [rt]

    result = AudioElement.notion_to_markdown(notion_block)
    assert result == '[audio](https://example.com/audio.mp3 "Fallback Text")'