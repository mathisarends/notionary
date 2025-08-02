"""
Pytest tests for DocumentElement.
Tests conversion between Markdown document embeds and Notion file blocks.
"""

import pytest
from notionary.blocks import DocumentElement


def test_match_markdown_valid_documents():
    assert DocumentElement.match_markdown("[document](https://example.com/doc.pdf)")
    assert DocumentElement.match_markdown(
        '[document](https://drive.google.com/file/d/123 "My Report")'
    )
    assert DocumentElement.match_markdown("   [document](https://abc.com/x.docx)   ")
    assert DocumentElement.match_markdown(
        '[document](https://example.com/y.xlsx "Finanzen Q4")'
    )


@pytest.mark.parametrize(
    "text",
    [
        "[document](https://test.de/abc.pdf)",
        '[document](https://host.com/hello.docx "Projektplan")',
        "  [document](https://server.net/file.pptx)  ",
        '[document](https://cloud.net/y.xlsx "Finanzen Q4")',
    ],
)
def test_match_markdown_param_valid(text):
    assert DocumentElement.match_markdown(text)


@pytest.mark.parametrize(
    "text",
    [
        "[doc](https://example.com/a.pdf)",  # falscher Prefix
        "[document](not-a-url)",  # ungültige URL
        "[document]()",  # kein Link
        "[document]( )",
        "![document](https://x.de/a.pdf)",
        "[document]https://example.com/a.pdf",  # fehlende Klammern
        "[document](ftp://site.com/file.pdf)",  # falsches Protokoll
        "",
        "random text",
    ],
)
def test_match_markdown_param_invalid(text):
    assert not DocumentElement.match_markdown(text)


def test_match_notion_block():
    assert DocumentElement.match_notion({"type": "file"})
    assert not DocumentElement.match_notion({"type": "paragraph"})
    assert not DocumentElement.match_notion({})
    assert not DocumentElement.match_notion({"type": "image"})


@pytest.mark.parametrize(
    "markdown, expected",
    [
        (
            '[document](https://docs.example.com/mydoc.pdf "Bericht 2024")',
            [
                {
                    "type": "file",
                    "file": {
                        "type": "external",
                        "external": {"url": "https://docs.example.com/mydoc.pdf"},
                        "caption": [
                            {"type": "text", "text": {"content": "Bericht 2024"}}
                        ],
                    },
                },
                {"type": "paragraph", "paragraph": {"rich_text": []}},
            ],
        ),
        (
            "[document](https://x.de/a.docx)",
            [
                {
                    "type": "file",
                    "file": {
                        "type": "external",
                        "external": {"url": "https://x.de/a.docx"},
                        "caption": [],
                    },
                },
                {"type": "paragraph", "paragraph": {"rich_text": []}},
            ],
        ),
    ],
)
def test_markdown_to_notion(markdown, expected):
    result = DocumentElement.markdown_to_notion(markdown)
    assert result == expected


def test_markdown_to_notion_invalid_cases():
    assert DocumentElement.markdown_to_notion("[doc](https://x.com/a.pdf)") is None
    assert DocumentElement.markdown_to_notion("[document]()") is None
    assert DocumentElement.markdown_to_notion("") is None
    assert DocumentElement.markdown_to_notion("nur Text") is None


def test_notion_to_markdown_with_caption():
    notion_block = {
        "type": "file",
        "file": {
            "type": "external",
            "external": {"url": "https://files.com/cv.pdf"},
            "caption": [{"type": "text", "text": {"content": "Mein Lebenslauf"}}],
        },
    }
    result = DocumentElement.notion_to_markdown(notion_block)
    assert result == '[document](https://files.com/cv.pdf "Mein Lebenslauf")'


def test_notion_to_markdown_without_caption():
    notion_block = {
        "type": "file",
        "file": {
            "type": "external",
            "external": {"url": "https://x.com/empty.pdf"},
            "caption": [],
        },
    }
    result = DocumentElement.notion_to_markdown(notion_block)
    assert result == "[document](https://x.com/empty.pdf)"


def test_notion_to_markdown_file_type():
    notion_block = {
        "type": "file",
        "file": {
            "type": "file",
            "file": {"url": "https://notion.com/file.doc"},
            "caption": [],
        },
    }
    result = DocumentElement.notion_to_markdown(notion_block)
    assert result == "[document](https://notion.com/file.doc)"


def test_notion_to_markdown_invalid_cases():
    assert DocumentElement.notion_to_markdown({"type": "paragraph"}) is None
    assert DocumentElement.notion_to_markdown({"type": "file"}) is None
    assert DocumentElement.notion_to_markdown({"type": "file", "file": {}}) is None
    block = {"type": "file", "file": {"type": "external", "external": {}}}
    assert DocumentElement.notion_to_markdown(block) is None


def test_extract_text_content():
    rt = [
        {"type": "text", "text": {"content": "Test "}},
        {"type": "text", "text": {"content": "Dokument"}},
    ]
    assert DocumentElement._extract_text_content(rt) == "Test Dokument"
    rt2 = [{"plain_text": "BackupText"}]
    assert DocumentElement._extract_text_content(rt2) == "BackupText"
    assert DocumentElement._extract_text_content([]) == ""


def test_is_multiline():
    assert not DocumentElement.is_multiline()


@pytest.mark.parametrize(
    "markdown",
    [
        '[document](https://a.com/file.pdf "Roundtrip Caption")',
        "[document](https://example.com/x.docx)",
        '[document](https://abc.de/y.pptx "Bericht 🙂")',
    ],
)
def test_roundtrip_conversion(markdown):
    notion_blocks = DocumentElement.markdown_to_notion(markdown)
    assert notion_blocks is not None
    notion_block = notion_blocks[0]
    back = DocumentElement.notion_to_markdown(notion_block)
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
    url = "https://host.de/x.pdf"
    markdown = f'[document]({url} "{caption}")' if caption else f"[document]({url})"
    blocks = DocumentElement.markdown_to_notion(markdown)
    assert blocks is not None
    document_block = blocks[0]
    roundtrip = DocumentElement.notion_to_markdown(document_block)
    assert roundtrip == markdown


def test_extra_whitespace_and_newlines():
    md = '   [document](https://x.com/d.pdf "  Caption with spaces   ")   '
    blocks = DocumentElement.markdown_to_notion(md)
    assert blocks is not None
    block = blocks[0]
    assert block["file"]["caption"][0]["text"]["content"] == "  Caption with spaces   "
    back = DocumentElement.notion_to_markdown(block)
    assert back == '[document](https://x.com/d.pdf "  Caption with spaces   ")'


def test_integration_with_other_elements():
    not_documents = [
        "# Heading",
        "Paragraph text",
        "[link](https://example.com)",
        "![](https://example.com/img.jpg)",
        "",
        "   ",
    ]
    for text in not_documents:
        assert not DocumentElement.match_markdown(text)
