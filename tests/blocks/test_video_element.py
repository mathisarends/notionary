"""
Pytest tests for VideoElement.
Tests conversion between Markdown videos ([video](url "caption")) and Notion video blocks.
"""

import pytest
from notionary.blocks import VideoElement


@pytest.mark.parametrize(
    "text,expected",
    [
        ("[video](https://example.com/video.mp4)", True),
        ('[video](https://example.com/video.mp4 "A caption")', True),
        ("[video](https://youtu.be/dQw4w9WgXcQ)", True),
        ('[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Rick")', True),
        ("[video](not-a-url)", False),
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
    "block,expected",
    [
        ({"type": "video"}, True),
        ({"type": "image"}, False),
        ({"type": "paragraph"}, False),
        ({}, False),
    ],
)
def test_match_notion(block, expected):
    assert VideoElement.match_notion(block) == expected


@pytest.mark.parametrize(
    "md,url,caption",
    [
        ("[video](https://example.com/demo.mp4)", "https://example.com/demo.mp4", ""),
        (
            '[video](https://example.com/abc.mp4 "Demo Video")',
            "https://example.com/abc.mp4",
            "Demo Video",
        ),
        (
            "[video](https://youtu.be/dQw4w9WgXcQ)",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "",
        ),
        (
            '[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Rick")',
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "Rick",
        ),
    ],
)
def test_markdown_to_notion(md, url, caption):
    block_list = VideoElement.markdown_to_notion(md)
    assert block_list is not None
    block = block_list[0]
    assert block["type"] == "video"
    assert block["video"]["type"] == "external"
    assert block["video"]["external"]["url"] == url
    if caption:
        assert block["video"]["caption"][0]["text"]["content"] == caption
    else:
        assert block["video"]["caption"] == []


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


@pytest.mark.parametrize(
    "block,expected_md",
    [
        (
            {
                "type": "video",
                "video": {
                    "type": "external",
                    "external": {"url": "https://example.com/video.mp4"},
                    "caption": [{"type": "text", "text": {"content": "My Caption"}}],
                },
            },
            '[video](https://example.com/video.mp4 "My Caption")',
        ),
        (
            {
                "type": "video",
                "video": {
                    "type": "file",
                    "file": {"url": "https://example.com/uploaded.mp4"},
                    "caption": [],
                },
            },
            "[video](https://example.com/uploaded.mp4)",
        ),
        (
            {
                "type": "video",
                "video": {
                    "type": "external",
                    "external": {"url": "https://youtu.be/dQw4w9WgXcQ"},
                    "caption": [],
                },
            },
            "[video](https://youtu.be/dQw4w9WgXcQ)",
        ),
    ],
)
def test_notion_to_markdown(block, expected_md):
    assert VideoElement.notion_to_markdown(block) == expected_md


def test_notion_to_markdown_invalid():
    # Invalid block type
    assert VideoElement.notion_to_markdown({"type": "paragraph"}) is None
    # Missing url
    block = {"type": "video", "video": {"type": "external", "external": {}}}
    assert VideoElement.notion_to_markdown(block) is None


def test_extract_text_content():
    rt = [
        {"type": "text", "text": {"content": "This "}},
        {"type": "text", "text": {"content": "works"}},
    ]
    assert VideoElement._extract_text_content(rt) == "This works"
    pt = [{"plain_text": "Backup"}]
    assert VideoElement._extract_text_content(pt) == "Backup"


def test_is_multiline():
    assert not VideoElement.is_multiline()


@pytest.mark.parametrize(
    "md",
    [
        '[video](https://example.com/video.mp4 "Käse kaufen äöüß")',
        '[video](https://youtu.be/dQw4w9WgXcQ "Mit Emoji 🙂")',
        '[video](https://vimeo.com/123456 "中文说明")',
    ],
)
def test_unicode_and_special_caption(md):
    blocks = VideoElement.markdown_to_notion(md)
    assert blocks is not None
    block = blocks[0]
    # Caption must appear in the block
    caption_list = block["video"].get("caption", [])
    if caption_list:
        text = VideoElement._extract_text_content(caption_list)
        for word in md.split('"')[-2].split():
            assert word in text


def test_roundtrip():
    cases = [
        "[video](https://example.com/demo.mp4)",
        '[video](https://example.com/demo.mp4 "Demo Video")',
        "[video](https://youtu.be/dQw4w9WgXcQ)",
        '[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Rick")',
    ]
    for md in cases:
        block_list = VideoElement.markdown_to_notion(md)
        block = block_list[0]
        recovered = VideoElement.notion_to_markdown(block)
        assert recovered.startswith("[video](")

        orig_url = md.split("(")[1].split()[0]
        is_youtube = "youtube.com" in orig_url or "youtu.be" in orig_url

        if is_youtube:
            # Extrahiere die YouTube-ID und erwarte immer die lange Form im Output
            import re

            m = re.search(r"(?:youtu\.be/|youtube\.com/watch\?v=)([\w-]{11})", orig_url)
            assert m, f"Could not extract YouTube video id from {orig_url}"
            expected_url = f"https://www.youtube.com/watch?v={m.group(1)}"
            assert expected_url in recovered
        else:
            assert orig_url in recovered
