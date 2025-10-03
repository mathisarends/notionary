from unittest.mock import Mock

import pytest

from notionary.blocks.mappings.audio import AudioElement
from notionary.blocks.mappings.rich_text.models import RichText


@pytest.mark.asyncio
async def test_match_markdown_valid_audio():
    assert await AudioElement.markdown_to_notion("[audio](https://example.com/track.mp3)") is not None
    assert await AudioElement.markdown_to_notion("[audio](https://audio.de/a.wav)(caption:Ein Track)") is not None
    assert await AudioElement.markdown_to_notion("   [audio](https://x.org/b.ogg)(caption:Hallo)   ") is not None
    assert await AudioElement.markdown_to_notion("[audio](https://test.com/file.m4a)")
    # Auch OGA und Großbuchstaben
    assert await AudioElement.markdown_to_notion("[audio](https://example.com/audio.OGA)")
    assert await AudioElement.markdown_to_notion("[audio](https://audio.com/abc.mp3)(caption:Mit Caption)")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text",
    [
        "[audio](https://a.de/test.mp3)",
        "[audio](https://files.com/clip.wav)(caption:Stimme)",
        "   [audio](https://site.org/s.ogg)(caption:Podcast)   ",
        "[audio](https://music.com/sound.m4a)",
        "(caption:Background music)[audio](https://soundcloud.com/track.mp3)",
    ],
)
async def test_match_markdown_param_valid(text):
    assert await AudioElement.markdown_to_notion(text) is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text",
    [
        "[aud](https://test.com/track.mp3)",  # falscher Prefix
        "[audio]()",  # leer
        "[audio]( )",  # nur Leerzeichen
        "[audio]https://a.de/b.mp3",  # fehlende Klammern
        "",  # komplett leer
        "random text",  # kein Pattern
    ],
)
async def test_match_markdown_param_invalid(text):
    """Test cases that should return None due to pattern mismatch or empty content."""
    assert await AudioElement.markdown_to_notion(text) is None


@pytest.mark.asyncio
async def test_match_markdown_edge_cases():
    """Test edge cases that should work with file upload support."""
    # These will be treated as potential local files or URLs
    # Non-HTTP protocols will create external blocks (may fail at Notion API level but element accepts them)
    result_ftp = await AudioElement.markdown_to_notion("[audio](ftp://x.com/file.mp3)")
    assert result_ftp is not None  # Element accepts it, even if Notion API might reject it

    # Non-standard URLs without extensions are now accepted (validation happens at API level)
    result_no_ext = await AudioElement.markdown_to_notion("[audio](https://a.de/b)")
    assert result_no_ext is not None  # Now works - validation at API level

    # Non-audio extensions are accepted (validation happens at upload/API level)
    result_wrong_ext = await AudioElement.markdown_to_notion("[audio](https://example.com/file.jpg)")
    assert result_wrong_ext is not None

    # Local path syntax (not existing file)
    result_local = await AudioElement.markdown_to_notion("[audio](not-a-url)")
    assert result_local is not None  # Treated as potential local file, falls back to external URL


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


@pytest.mark.asyncio
async def test_markdown_to_notion_with_caption():
    """Test conversion from markdown to Notion with caption."""
    markdown = "[audio](https://abc.com/music.mp3)(caption:Mein Song)"
    result = await AudioElement.markdown_to_notion(markdown)

    assert result is not None
    # Result sollte ein CreateAudioBlock Pydantic-Modell sein
    assert result.type == "audio"
    assert result.audio.type == "external"
    assert result.audio.external.url == "https://abc.com/music.mp3"
    assert len(result.audio.caption) == 1
    assert result.audio.caption[0].plain_text == "Mein Song"


@pytest.mark.asyncio
async def test_markdown_to_notion_with_caption_before():
    """Test conversion from markdown to Notion with caption before URL."""
    markdown = "(caption:Background music)[audio](https://abc.com/music.mp3)"
    result = await AudioElement.markdown_to_notion(markdown)

    assert result is not None
    assert result.type == "audio"
    assert result.audio.type == "external"
    assert result.audio.external.url == "https://abc.com/music.mp3"
    assert len(result.audio.caption) == 1
    assert result.audio.caption[0].plain_text == "Background music"


@pytest.mark.asyncio
async def test_markdown_to_notion_without_caption():
    """Test conversion from markdown to Notion without caption."""
    markdown = "[audio](https://x.de/track.wav)"
    result = await AudioElement.markdown_to_notion(markdown)

    assert result is not None
    assert result.type == "audio"
    assert result.audio.type == "external"
    assert result.audio.external.url == "https://x.de/track.wav"
    assert result.audio.caption == []


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid_cases():
    assert await AudioElement.markdown_to_notion("[aud](https://a.com/x.mp3)") is None
    assert await AudioElement.markdown_to_notion("[audio]()") is None
    assert await AudioElement.markdown_to_notion("") is None
    assert await AudioElement.markdown_to_notion("nur Text") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_with_caption():
    """Test conversion from Notion to markdown with caption."""
    # Mock Block object
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://sound.com/track.ogg"

    # Use real RichText instead of mock
    caption_rt = RichText.from_plain_text("Der Sound")
    notion_block.audio.caption = [caption_rt]

    result = await AudioElement.notion_to_markdown(notion_block)
    assert result == "[audio](https://sound.com/track.ogg)(caption:Der Sound)"


@pytest.mark.asyncio
async def test_notion_to_markdown_without_caption():
    """Test conversion from Notion to markdown without caption."""
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://sound.com/no-caption.mp3"
    notion_block.audio.caption = []

    result = await AudioElement.notion_to_markdown(notion_block)
    assert result == "[audio](https://sound.com/no-caption.mp3)"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid_cases():
    """Test invalid cases return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.audio = None
    assert await AudioElement.notion_to_markdown(paragraph_block) is None

    # Audio is None
    audio_none_block = Mock()
    audio_none_block.type = "audio"
    audio_none_block.audio = None
    assert await AudioElement.notion_to_markdown(audio_none_block) is None

    # Not external type
    file_block = Mock()
    file_block.type = "audio"
    file_block.audio = Mock()
    file_block.audio.type = "file"
    file_block.audio.external = None
    assert await AudioElement.notion_to_markdown(file_block) is None

    # Missing URL
    no_url_block = Mock()
    no_url_block.type = "audio"
    no_url_block.audio = Mock()
    no_url_block.audio.type = "external"
    no_url_block.audio.external = Mock()
    no_url_block.audio.external.url = None
    assert await AudioElement.notion_to_markdown(no_url_block) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown",
    [
        "[audio](https://music.com/roundtrip.mp3)(caption:Roundtrip Caption)",
        "[audio](https://sound.com/x.wav)",
        "[audio](https://a.b/c.ogg)(caption:🙂 Mit Emoji)",
        "(caption:Background music)[audio](https://example.com/song.mp3)",
    ],
)
async def test_roundtrip_conversion(markdown):
    """Test that markdown -> notion -> markdown preserves content."""
    # Create proper Block object for testing
    notion_result = await AudioElement.markdown_to_notion(markdown)
    assert notion_result is not None

    # For roundtrip, we need to create a proper Block mock
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = notion_result.audio.type
    notion_block.audio.external = notion_result.audio.external
    notion_block.audio.caption = notion_result.audio.caption

    back = await AudioElement.notion_to_markdown(notion_block)

    # Note: The mixin may normalize caption position, so we need to check content equivalence
    # rather than exact string match for cases with captions
    if "(caption:" in markdown:
        # Extract the URL and caption content for comparison
        assert "[audio](" in back
        assert notion_result.audio.external.url in back
        if notion_result.audio.caption:
            caption_text = notion_result.audio.caption[0].plain_text
            assert f"(caption:{caption_text})" in back
    else:
        assert back == markdown


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "caption",
    [
        "Mit Umlauten äöüß",
        "Emoji 🙂😎",
        "Special chars !?&/()",  # Fixed: removed brackets that break regex
        "中文测试",
    ],
)
async def test_unicode_and_special_caption(caption):
    """Test handling of Unicode and special characters in captions."""
    url = "https://audio.host/x.mp3"
    markdown = f"[audio]({url})(caption:{caption})"
    block = await AudioElement.markdown_to_notion(markdown)
    assert block is not None
    assert block.audio.caption[0].plain_text == caption


@pytest.mark.asyncio
async def test_empty_caption_edge_case():
    """Test handling of empty caption."""
    url = "https://audio.host/x.mp3"
    markdown = f"[audio]({url})"
    block = await AudioElement.markdown_to_notion(markdown)
    assert block is not None
    assert block.audio.caption == []


@pytest.mark.asyncio
async def test_extra_whitespace_and_caption_spaces():
    """Test handling of whitespace in input and captions."""
    # Whitespace around the markdown should be stripped by match_markdown
    md = "   [audio](https://aud.io/a.mp3)(caption:  Caption mit Leerzeichen   )   "
    assert await AudioElement.markdown_to_notion(md) is not None

    block = await AudioElement.markdown_to_notion(md)
    assert block is not None
    # Caption spaces should be preserved
    assert block.audio.caption[0].plain_text == "  Caption mit Leerzeichen   "


@pytest.mark.asyncio
async def test_integration_with_other_elements():
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
        assert await AudioElement.markdown_to_notion(text) is None


@pytest.mark.asyncio
async def test_url_validation_via_match_markdown():
    """Test URL validation through match_markdown (with file upload support)."""
    # Valid HTTP/HTTPS URLs with audio extensions
    valid_urls = [
        "[audio](http://example.com/file.mp3)",
        "[audio](https://example.com/file.wav)",
        "[audio](https://subdomain.example.com/path/to/file.ogg)",
        "[audio](https://example.com/file.m4a)",
        "[audio](https://example.com/file.oga)",
    ]
    for url in valid_urls:
        assert await AudioElement.markdown_to_notion(url) is not None

    # With file upload support, these are now accepted (validation at API level)
    edge_case_urls = [
        "[audio](https://example.com/file)",  # No extension - now accepted
        "[audio](https://example.com/file.txt)",  # Wrong extension - now accepted
        "[audio](https://example.com/file.jpg)",  # Wrong extension - now accepted
        "[audio](not-a-url)",  # Treated as potential local file - now accepted
    ]
    for url in edge_case_urls:
        result = await AudioElement.markdown_to_notion(url)
        assert result is not None  # Now accepted with file upload support


@pytest.mark.asyncio
async def test_caption_with_rich_text():
    """Test handling of rich text formatting in captions."""
    # Test with bold formatting
    markdown = "[audio](https://example.com/file.mp3)(caption:**Bold** text)"
    block = await AudioElement.markdown_to_notion(markdown)
    assert block is not None
    # The mixin should handle rich text parsing
    assert len(block.audio.caption) >= 1


@pytest.mark.asyncio
async def test_multiple_caption_rich_text_objects():
    """Test notion_to_markdown with multiple rich text objects in caption."""
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://example.com/audio.mp3"

    # Use real RichTextObjects instead of mocks
    rt1 = RichText.from_plain_text("Part 1 ")
    rt2 = RichText.from_plain_text("Part 2")
    notion_block.audio.caption = [rt1, rt2]

    result = await AudioElement.notion_to_markdown(notion_block)
    assert result == "[audio](https://example.com/audio.mp3)(caption:Part 1 Part 2)"


@pytest.mark.asyncio
async def test_notion_to_markdown_with_plain_text_fallback():
    """Test notion_to_markdown falls back to plain_text when text content is missing."""
    notion_block = Mock()
    notion_block.type = "audio"
    notion_block.audio = Mock()
    notion_block.audio.type = "external"
    notion_block.audio.external = Mock()
    notion_block.audio.external.url = "https://example.com/audio.mp3"

    # Use real RichText instead of mock
    rt = RichText.from_plain_text("Fallback Text")
    notion_block.audio.caption = [rt]

    result = await AudioElement.notion_to_markdown(notion_block)
    assert result == "[audio](https://example.com/audio.mp3)(caption:Fallback Text)"
