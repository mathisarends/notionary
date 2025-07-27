import pytest
from notionary.blocks import AudioElement

def test_match_markdown_valid_audio():
    assert AudioElement.match_markdown('[audio](https://example.com/track.mp3)')
    assert AudioElement.match_markdown('[audio](https://audio.de/a.wav "Ein Track")')
    assert AudioElement.match_markdown('   [audio](https://x.org/b.ogg "Hallo")   ')
    assert AudioElement.match_markdown('[audio](https://test.com/file.m4a)')
    # Auch OGA und Großbuchstaben
    assert AudioElement.match_markdown('[audio](https://example.com/audio.OGA)')
    assert AudioElement.match_markdown('[audio](https://audio.com/abc.mp3 "Mit Caption")')

@pytest.mark.parametrize(
    "text",
    [
        '[audio](https://a.de/test.mp3)',
        '[audio](https://files.com/clip.wav "Stimme")',
        '   [audio](https://site.org/s.ogg "Podcast")   ',
        '[audio](https://music.com/sound.m4a)',
    ]
)
def test_match_markdown_param_valid(text):
    assert AudioElement.match_markdown(text)

@pytest.mark.parametrize(
    "text",
    [
        '[aud](https://test.com/track.mp3)',       # falscher Prefix
        '[audio](not-a-url)',                      # kein URL
        '[audio]()',                               # leer
        '[audio]( )',
        '[audio](ftp://x.com/file.mp3)',           # falsches Protokoll
        '[audio]https://a.de/b.mp3',               # fehlende Klammern
        '[audio](https://a.de/b)',                 # keine Extension
        '[audio](https://example.com/file.jpg)',   # kein Audio
        '![audio](https://example.com/file.mp3)',  # falsches Präfix
        '',
        'random text',
    ]
)
def test_match_markdown_param_invalid(text):
    assert not AudioElement.match_markdown(text)

def test_match_notion_block():
    assert AudioElement.match_notion({"type": "audio"})
    assert not AudioElement.match_notion({"type": "paragraph"})
    assert not AudioElement.match_notion({})
    assert not AudioElement.match_notion({"type": "image"})

@pytest.mark.parametrize(
    "markdown, expected",
    [
        (
            '[audio](https://abc.com/music.mp3 "Mein Song")',
            {
                "type": "audio",
                "audio": {
                    "type": "external",
                    "external": {"url": "https://abc.com/music.mp3"},
                    "caption": [
                        {
                            "type": "text",
                            "text": {"content": "Mein Song", "link": None},
                            "annotations": {
                                "bold": False,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "Mein Song",
                            "href": None,
                        }
                    ],
                },
            }
        ),
        (
            "[audio](https://x.de/track.wav)",
            {
                "type": "audio",
                "audio": {
                    "type": "external",
                    "external": {"url": "https://x.de/track.wav"},
                    "caption": [],
                },
            }
        ),
    ]
)
def test_markdown_to_notion(markdown, expected):
    result = AudioElement.markdown_to_notion(markdown)
    assert result == expected

def test_markdown_to_notion_invalid_cases():
    assert AudioElement.markdown_to_notion('[aud](https://a.com/x.mp3)') is None
    assert AudioElement.markdown_to_notion('[audio]()') is None
    assert AudioElement.markdown_to_notion('') is None
    assert AudioElement.markdown_to_notion('nur Text') is None

def test_notion_to_markdown_with_caption():
    notion_block = {
        "type": "audio",
        "audio": {
            "type": "external",
            "external": {"url": "https://sound.com/track.ogg"},
            "caption": [
                {
                    "type": "text",
                    "text": {"content": "Der Sound"},
                    "annotations": {
                        "bold": False, "italic": False, "strikethrough": False,
                        "underline": False, "code": False, "color": "default"
                    },
                    "plain_text": "Der Sound",
                    "href": None,
                }
            ],
        },
    }
    result = AudioElement.notion_to_markdown(notion_block)
    assert result == '[audio](https://sound.com/track.ogg "Der Sound")'


def test_notion_to_markdown_without_caption():
    notion_block = {
        "type": "audio",
        "audio": {
            "type": "external",
            "external": {"url": "https://sound.com/no-caption.mp3"},
            "caption": [],
        },
    }
    result = AudioElement.notion_to_markdown(notion_block)
    assert result == "[audio](https://sound.com/no-caption.mp3)"

def test_notion_to_markdown_invalid_cases():
    assert AudioElement.notion_to_markdown({"type": "paragraph"}) is None
    assert AudioElement.notion_to_markdown({"type": "audio"}) is None
    assert AudioElement.notion_to_markdown({"type": "audio", "audio": {}}) is None
    block = {"type": "audio", "audio": {"type": "external", "external": {}}}
    assert AudioElement.notion_to_markdown(block) is None

def test_extract_text_content():
    rt = [
        {"type": "text", "text": {"content": "Test "}},
        {"type": "text", "text": {"content": "Audio"}},
    ]
    assert AudioElement._extract_text_content(rt) == "Test Audio"
    rt2 = [{"plain_text": "BackupText"}]
    assert AudioElement._extract_text_content(rt2) == "BackupText"
    assert AudioElement._extract_text_content([]) == ""

def test_is_multiline():
    assert not AudioElement.is_multiline()

@pytest.mark.parametrize(
    "markdown",
    [
        '[audio](https://music.com/roundtrip.mp3 "Roundtrip Caption")',
        "[audio](https://sound.com/x.wav)",
        '[audio](https://a.b/c.ogg "🙂 Mit Emoji")',
    ]
)
def test_roundtrip_conversion(markdown):
    notion_block = AudioElement.markdown_to_notion(markdown)
    assert notion_block is not None
    back = AudioElement.notion_to_markdown(notion_block)
    assert back == markdown

@pytest.mark.parametrize(
    "caption",
    [
        "Mit Umlauten äöüß",
        "Emoji 🙂😎",
        "Special chars !?&/()[]",
        "中文测试",
        "",
    ]
)
def test_unicode_and_special_caption(caption):
    url = "https://audio.host/x.mp3"
    markdown = f'[audio]({url} "{caption}")' if caption else f"[audio]({url})"
    block = AudioElement.markdown_to_notion(markdown)
    assert block is not None
    back = AudioElement.notion_to_markdown(block)
    assert back == markdown

def test_extra_whitespace_and_newlines():
    md = '   [audio](https://aud.io/a.mp3 "  Caption mit Leerzeichen   ")   '
    block = AudioElement.markdown_to_notion(md)
    assert block is not None
    # Caption muss Spaces behalten
    assert block["audio"]["caption"][0]["text"]["content"] == "  Caption mit Leerzeichen   "
    back = AudioElement.notion_to_markdown(block)
    assert back == '[audio](https://aud.io/a.mp3 "  Caption mit Leerzeichen   ")'

def test_integration_with_other_elements():
    not_audio = [
        "# Heading",
        "Paragraph text",
        "[link](https://example.com)",
        "[image](https://img.com/b.jpg)",
        "",
        "   ",
    ]
    for text in not_audio:
        assert not AudioElement.match_markdown(text)
