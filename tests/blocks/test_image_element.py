"""
Pytest tests for ImageElement.
Tests conversion between Markdown images and Notion image blocks.
"""

import pytest
from notionary.blocks.image_block import ImageElement


def test_match_markdown_valid_images():
    """Test recognition of valid Markdown image formats."""
    assert ImageElement.match_markdown("[image](https://example.com/img.jpg)")
    assert ImageElement.match_markdown(
        '[image](https://example.com/img.jpg "A caption")'
    )
    assert ImageElement.match_markdown('[image](https://cdn.net/pic.png "Logo")')
    assert ImageElement.match_markdown("[image](https://a.de/b.jpg)")
    # Whitespace is trimmed
    assert ImageElement.match_markdown("   [image](https://example.com/img.jpg)   ")


@pytest.mark.parametrize(
    "text",
    [
        "[image](https://example.com/img.jpg)",
        '[image](https://example.com/img.jpg "My caption")',
        '[image](https://cdn.com/photo.png "Logo 123")',
        '   [image](https://xx.com/a.png "Hello")  ',
    ],
)
def test_match_markdown_param_valid(text):
    assert ImageElement.match_markdown(text)


@pytest.mark.parametrize(
    "text",
    [
        "[img](https://example.com/img.jpg)",  # Wrong prefix
        "[image](not-a-url)",  # Invalid URL
        "[image](ftp://site.com/img.jpg)",  # Wrong scheme
        "[image]()",
        "[image]( )",
        "![image](https://example.com/img.jpg)",  # Markdown classic
        "[image]https://example.com/img.jpg",  # Missing parens
        "[image](https://example.com/img.jpg)",  # Valid, for control
        "[image](https://example.com/img.jpg 'caption')",  # Wrong quotes
        "no image here",
    ],
)
def test_match_markdown_param_invalid(text):
    # Should be false except for the valid control
    expected = (
        text.strip().startswith("[image](")
        and text.count('"') in (0, 2)
        and text.startswith("[image](")
    )
    result = ImageElement.match_markdown(text)
    if text == "[image](https://example.com/img.jpg)":
        assert result
    else:
        assert not result


def test_match_notion_block():
    """Test recognition of Notion image blocks."""
    assert ImageElement.match_notion({"type": "image"})
    assert not ImageElement.match_notion({"type": "paragraph"})
    assert not ImageElement.match_notion({})
    assert not ImageElement.match_notion({"type": "file"})
    assert not ImageElement.match_notion({"block": "image"})


@pytest.mark.parametrize(
    "markdown, expected",
    [
        (
            '[image](https://example.com/a.jpg "A caption")',
            [
                {
                    "type": "image",
                    "image": {
                        "type": "external",
                        "external": {"url": "https://example.com/a.jpg"},
                        "caption": [{"type": "text", "text": {"content": "A caption"}}],
                    },
                },
                {"type": "paragraph", "paragraph": {"rich_text": []}},
            ],
        ),
        (
            "[image](https://example.com/only-url.jpg)",
            [
                {
                    "type": "image",
                    "image": {
                        "type": "external",
                        "external": {"url": "https://example.com/only-url.jpg"},
                        "caption": [],
                    },
                },
                {"type": "paragraph", "paragraph": {"rich_text": []}},
            ],
        ),
    ],
)
def test_markdown_to_notion(markdown, expected):
    result = ImageElement.markdown_to_notion(markdown)
    assert result == expected


def test_markdown_to_notion_invalid_cases():
    # Not a valid markdown image
    assert ImageElement.markdown_to_notion("[img](https://example.com/a.jpg)") is None
    # Missing URL
    assert ImageElement.markdown_to_notion("[image]()") is None
    # Empty
    assert ImageElement.markdown_to_notion("") is None
    # Not even markdown
    assert ImageElement.markdown_to_notion("Just a text") is None


def test_notion_to_markdown_external_with_caption():
    notion_block = {
        "type": "image",
        "image": {
            "type": "external",
            "external": {"url": "https://cdn.net/cat.png"},
            "caption": [{"type": "text", "text": {"content": "The Cat"}}],
        },
    }
    result = ImageElement.notion_to_markdown(notion_block)
    assert result == '[image](https://cdn.net/cat.png "The Cat")'


def test_notion_to_markdown_external_without_caption():
    notion_block = {
        "type": "image",
        "image": {
            "type": "external",
            "external": {"url": "https://cdn.net/no-caption.png"},
            "caption": [],
        },
    }
    result = ImageElement.notion_to_markdown(notion_block)
    assert result == "[image](https://cdn.net/no-caption.png)"


def test_notion_to_markdown_file_type():
    notion_block = {
        "type": "image",
        "image": {
            "type": "file",
            "file": {"url": "https://notion.com/uploads/dog.jpg"},
            "caption": [],
        },
    }
    result = ImageElement.notion_to_markdown(notion_block)
    assert result == "[image](https://notion.com/uploads/dog.jpg)"


def test_notion_to_markdown_invalid_cases():
    # Not an image type
    assert ImageElement.notion_to_markdown({"type": "paragraph"}) is None
    # Missing image
    assert ImageElement.notion_to_markdown({"type": "image"}) is None
    # Invalid image structure
    assert ImageElement.notion_to_markdown({"type": "image", "image": {}}) is None
    # Missing url
    block = {"type": "image", "image": {"type": "external", "external": {}}}
    assert ImageElement.notion_to_markdown(block) is None


def test_extract_text_content():
    # Rich text list with content
    rt = [
        {"type": "text", "text": {"content": "A "}},
        {"type": "text", "text": {"content": "caption"}},
    ]
    assert ImageElement._extract_text_content(rt) == "A caption"

    # Plain text field only
    rt2 = [{"plain_text": "Test123"}]
    assert ImageElement._extract_text_content(rt2) == "Test123"

    # Mixed/empty
    assert ImageElement._extract_text_content([]) == ""


def test_is_multiline():
    assert not ImageElement.is_multiline()


@pytest.mark.parametrize(
    "markdown",
    [
        '[image](https://example.com/roundtrip.jpg "Roundtrip Caption")',
        "[image](https://example.com/x.jpg)",
        '[image](https://a.b/c.png "🙂 Emoji")',
    ],
)
def test_roundtrip_conversion(markdown):
    # Markdown -> Notion -> Markdown roundtrip
    notion_blocks = ImageElement.markdown_to_notion(markdown)
    assert notion_blocks is not None
    notion_block = notion_blocks[0]
    back = ImageElement.notion_to_markdown(notion_block)
    # Roundtrip only works if there is or isn't a caption consistently
    assert back == markdown


@pytest.mark.parametrize(
    "caption",
    [
        "Mit Umlauten äöüß",
        "Emoji 🙂😎",
        "Special chars !?&/()[]",
        "中文测试",
        "",
    ],
)
def test_unicode_and_special_caption(caption):
    url = "https://host.de/x.png"
    markdown = f'[image]({url} "{caption}")' if caption else f"[image]({url})"
    blocks = ImageElement.markdown_to_notion(markdown)
    assert blocks is not None
    image_block = blocks[0]
    # Check caption is present or not
    roundtrip = ImageElement.notion_to_markdown(image_block)
    assert roundtrip == markdown


def test_multiple_images_independent():
    """Ensure each image is parsed independently."""
    images = [
        '[image](https://a.de/1.jpg "One")',
        "[image](https://a.de/2.jpg)",
        '[image](https://a.de/3.jpg "Three")',
    ]
    for md in images:
        result = ImageElement.markdown_to_notion(md)
        assert result is not None
        block = result[0]
        assert block["type"] == "image"
        assert "image" in block
        url = block["image"].get("external", {}).get("url", "") or block["image"].get(
            "file", {}
        ).get("url", "")
        assert url.startswith("https://a.de/")
        back = ImageElement.notion_to_markdown(block)
        assert back == md


def test_extra_whitespace_and_newlines():
    """Test whitespace trimming in image markdown."""
    md = '   [image](https://ab.com/c.jpg "  Caption with spaces   ")   '
    blocks = ImageElement.markdown_to_notion(md)
    assert blocks is not None
    block = blocks[0]
    # Caption should be preserved with spaces inside quotes
    assert block["image"]["caption"][0]["text"]["content"] == "  Caption with spaces   "
    back = ImageElement.notion_to_markdown(block)
    assert back == '[image](https://ab.com/c.jpg "  Caption with spaces   ")'


def test_integration_with_other_elements():
    """Ensure ImageElement does not falsely match non-image markdown."""
    not_images = [
        "# Heading",
        "Paragraph text",
        "[link](https://example.com)",
        "![](https://example.com/img.jpg)",
        "",
        "   ",
    ]
    for text in not_images:
        assert not ImageElement.match_markdown(text)


# Optional: fixtures for reusability (not strictly needed for image, but for symmetry)
@pytest.fixture
def external_image_block():
    return {
        "type": "image",
        "image": {
            "type": "external",
            "external": {"url": "https://cdn.net/test.png"},
            "caption": [{"type": "text", "text": {"content": "Hello"}}],
        },
    }


@pytest.fixture
def file_image_block():
    return {
        "type": "image",
        "image": {
            "type": "file",
            "file": {"url": "https://notion.com/file.jpg"},
            "caption": [],
        },
    }


def test_fixtures_external(external_image_block):
    result = ImageElement.notion_to_markdown(external_image_block)
    assert result == '[image](https://cdn.net/test.png "Hello")'


def test_fixtures_file(file_image_block):
    result = ImageElement.notion_to_markdown(file_image_block)
    assert result == "[image](https://notion.com/file.jpg)"
