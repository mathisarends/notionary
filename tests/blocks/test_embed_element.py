import pytest
from notionary.blocks import EmbedElement


@pytest.mark.parametrize(
    "text,expected",
    [
        ("[embed](https://example.com)", True),
        ('[embed](https://example.com "A caption")', True),
        ("[embed](https://drive.google.com/file/d/12345/view)", True),
        ('[embed](https://twitter.com/NotionHQ/status/123 "Tweet")', True),
        ("[embed](not-a-url)", False),
        ("[embed]()", False),
        ("[embed](   )", False),
        ("[embd](https://example.com)", False),
        ("![embed](https://example.com)", False),
        ("Just text", False),
        ("", False),
    ],
)
def test_match_markdown(text, expected):
    assert EmbedElement.match_markdown(text) == expected


@pytest.mark.parametrize(
    "block,expected",
    [
        ({"type": "embed"}, True),
        ({"type": "image"}, False),
        ({"type": "paragraph"}, False),
        ({}, False),
    ],
)
def test_match_notion(block, expected):
    assert EmbedElement.match_notion(block) == expected


@pytest.mark.parametrize(
    "md,url,caption",
    [
        ("[embed](https://example.com)", "https://example.com", ""),
        ('[embed](https://github.com "Repo")', "https://github.com", "Repo"),
        (
            '[embed](https://twitter.com/NotionHQ/status/123 "Tweet")',
            "https://twitter.com/NotionHQ/status/123",
            "Tweet",
        ),
        ('[embed](https://maps.google.com "Map")', "https://maps.google.com", "Map"),
    ],
)
def test_markdown_to_notion(md, url, caption):
    block_list = EmbedElement.markdown_to_notion(md)
    assert block_list is not None
    block = block_list[0]
    assert block["type"] == "embed"
    assert block["embed"]["url"] == url
    if caption:
        assert block["embed"]["caption"][0]["text"]["content"] == caption
    else:
        assert block["embed"]["caption"] == []


@pytest.mark.parametrize(
    "md",
    [
        "[embed]()",
        "[embed](not-a-url)",
        "[embed](   )",
        "not an embed",
        "",
    ],
)
def test_markdown_to_notion_invalid(md):
    assert EmbedElement.markdown_to_notion(md) is None


@pytest.mark.parametrize(
    "block,expected_md",
    [
        (
            {
                "type": "embed",
                "embed": {
                    "url": "https://example.com",
                    "caption": [{"type": "text", "text": {"content": "My Caption"}}],
                },
            },
            '[embed](https://example.com "My Caption")',
        ),
        (
            {
                "type": "embed",
                "embed": {
                    "url": "https://github.com",
                    "caption": [],
                },
            },
            "[embed](https://github.com)",
        ),
    ],
)
def test_notion_to_markdown(block, expected_md):
    assert EmbedElement.notion_to_markdown(block) == expected_md


def test_notion_to_markdown_invalid():
    assert EmbedElement.notion_to_markdown({"type": "paragraph"}) is None
    block = {"type": "embed", "embed": {"url": ""}}
    assert EmbedElement.notion_to_markdown(block) is None


def test_extract_text_content():
    rt = [
        {"type": "text", "text": {"content": "This "}},
        {"type": "text", "text": {"content": "works"}},
    ]
    assert EmbedElement._extract_text_content(rt) == "This works"
    pt = [{"plain_text": "Backup"}]
    assert EmbedElement._extract_text_content(pt) == "Backup"


def test_is_multiline():
    assert not EmbedElement.is_multiline()


@pytest.mark.parametrize(
    "md",
    [
        '[embed](https://example.com "Käse kaufen äöüß")',
        '[embed](https://twitter.com/NotionHQ/status/123 "Mit Emoji 🙂")',
        '[embed](https://vimeo.com/123456 "中文说明")',
    ],
)
def test_unicode_and_special_caption(md):
    blocks = EmbedElement.markdown_to_notion(md)
    assert blocks is not None
    block = blocks[0]
    caption_list = block["embed"].get("caption", [])
    if caption_list:
        text = EmbedElement._extract_text_content(caption_list)
        for word in md.split('"')[-2].split():
            assert word in text


def test_roundtrip():
    cases = [
        "[embed](https://example.com)",
        '[embed](https://example.com "Demo Embed")',
        "[embed](https://github.com)",
        '[embed](https://twitter.com/NotionHQ/status/123 "Tweet")',
    ]
    for md in cases:
        block_list = EmbedElement.markdown_to_notion(md)
        block = block_list[0]
        recovered = EmbedElement.notion_to_markdown(block)
        assert recovered.startswith("[embed](")
        url = md.split("(")[1].split()[0]
        assert url in recovered
