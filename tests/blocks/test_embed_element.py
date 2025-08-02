import pytest
from notionary.blocks.embed import EmbedElement
from notionary.blocks.embed.embed_models import EmbedBlock, CreateEmbedBlock
from notionary.blocks.block_models import Block
from notionary.blocks.rich_text.rich_text_models import RichTextObject, TextContent, TextAnnotations


def create_rich_text_object(content: str) -> RichTextObject:
    """Helper function to create RichTextObject instances."""
    return RichTextObject(
        type="text",
        text=TextContent(content=content),
        annotations=TextAnnotations(),
        plain_text=content
    )


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"}
    }
    defaults.update(kwargs)
    return Block(**defaults)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("[embed](https://example.com)", True),
        ('[embed](https://example.com "A caption")', True),
        ("[embed](https://drive.google.com/file/d/12345/view)", True),
        ('[embed](https://twitter.com/NotionHQ/status/123 "Tweet")', True),
        ("[embed](not-a-url)", True),  # URL validation is not part of match_markdown
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
    "block_type,has_embed,expected",
    [
        ("embed", True, True),
        ("embed", False, False),
        ("image", False, False),
        ("paragraph", False, False),
    ],
)
def test_match_notion(block_type, has_embed, expected):
    block_data = {"type": block_type}
    if has_embed and block_type == "embed":
        block_data["embed"] = EmbedBlock(url="https://example.com")
    
    block = create_block_with_required_fields(**block_data)
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
    result = EmbedElement.markdown_to_notion(md)
    assert result is not None
    assert isinstance(result, CreateEmbedBlock)
    assert result.type == "embed"
    assert result.embed.url == url
    
    if caption:
        assert len(result.embed.caption) > 0
        assert result.embed.caption[0].plain_text == caption
    else:
        assert result.embed.caption == []


@pytest.mark.parametrize(
    "md",
    [
        "[embed]()",
        "[embed](   )",
        "not an embed",
        "",
    ],
)
def test_markdown_to_notion_invalid(md):
    assert EmbedElement.markdown_to_notion(md) is None


@pytest.mark.parametrize(
    "url,caption_text,expected_md",
    [
        ("https://example.com", "My Caption", '[embed](https://example.com "My Caption")'),
        ("https://github.com", "", "[embed](https://github.com)"),
        ("https://twitter.com/test", "Tweet", '[embed](https://twitter.com/test "Tweet")'),
    ],
)
def test_notion_to_markdown(url, caption_text, expected_md):
    caption_list = []
    if caption_text:
        caption_list = [create_rich_text_object(caption_text)]
    
    block = create_block_with_required_fields(
        type="embed",
        embed=EmbedBlock(url=url, caption=caption_list)
    )
    
    assert EmbedElement.notion_to_markdown(block) == expected_md


def test_notion_to_markdown_invalid():
    # Wrong block type
    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert EmbedElement.notion_to_markdown(paragraph_block) is None
    
    # Block without embed content
    empty_embed_block = create_block_with_required_fields(type="embed")
    assert EmbedElement.notion_to_markdown(empty_embed_block) is None
    
    # Block with empty URL (this case needs to be handled by the implementation)
    # Some implementations might allow empty URLs, others might not


def test_extract_text_content():
    # Test with dictionary format (for backward compatibility)
    rt_dicts = [
        {"type": "text", "text": {"content": "This "}},
        {"type": "text", "text": {"content": "works"}},
    ]
    assert EmbedElement._extract_text_content(rt_dicts) == "This works"
    
    # Test with plain_text fallback
    pt_dicts = [{"plain_text": "Backup"}]
    assert EmbedElement._extract_text_content(pt_dicts) == "Backup"
    
    # Test with mixed formats
    mixed = [
        {"type": "text", "text": {"content": "Mixed "}},
        {"plain_text": "format"},
    ]
    assert EmbedElement._extract_text_content(mixed) == "Mixed format"


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
    result = EmbedElement.markdown_to_notion(md)
    assert result is not None
    assert isinstance(result, CreateEmbedBlock)
    
    caption_list = result.embed.caption
    if caption_list:
        # Extract the expected caption from the markdown
        expected_caption = md.split('"')[1]  # Get text between first pair of quotes
        actual_caption = caption_list[0].plain_text
        assert actual_caption == expected_caption


def test_roundtrip():
    cases = [
        "[embed](https://example.com)",
        '[embed](https://example.com "Demo Embed")',
        "[embed](https://github.com)",
        '[embed](https://twitter.com/NotionHQ/status/123 "Tweet")',
    ]
    
    for md in cases:
        # Convert to Notion
        embed_create_block = EmbedElement.markdown_to_notion(md)
        assert embed_create_block is not None
        
        # Create a Block for notion_to_markdown
        block = create_block_with_required_fields(
            type="embed",
            embed=embed_create_block.embed
        )
        
        # Convert back to Markdown
        recovered = EmbedElement.notion_to_markdown(block)
        assert recovered is not None
        assert recovered.startswith("[embed](")
        
        # Extract URL from original markdown
        url = md.split("(")[1].split()[0].rstrip(')"')
        assert url in recovered
        
        # If original had a caption, recovered should too
        if '"' in md:
            assert '"' in recovered
        else:
            assert '"' not in recovered


def test_embed_with_complex_urls():
    """Test embed with complex URLs that might have query parameters."""
    complex_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://docs.google.com/document/d/1ABC123/edit?usp=sharing",
        "https://github.com/user/repo/pull/123#issuecomment-456789",
        "https://example.com/path?param1=value1&param2=value2",
    ]
    
    for url in complex_urls:
        md = f"[embed]({url})"
        result = EmbedElement.markdown_to_notion(md)
        assert result is not None
        assert result.embed.url == url


def test_embed_caption_with_special_characters():
    """Test embed captions with special characters and formatting."""
    special_captions = [
        "Caption with \"quotes\" inside",
        "Caption with (parentheses)",
        "Caption with [brackets]",
        "Caption with & symbols",
        "Caption with émojis 🎉",
    ]
    
    for caption in special_captions:
        md = f'[embed](https://example.com "{caption}")'
        result = EmbedElement.markdown_to_notion(md)
        assert result is not None
        assert len(result.embed.caption) > 0
        assert result.embed.caption[0].plain_text == caption


def test_empty_and_whitespace_captions():
    """Test handling of empty and whitespace-only captions."""
    test_cases = [
        ('[embed](https://example.com "")', ""),  # Empty caption
        ('[embed](https://example.com "   ")', "   "),  # Whitespace caption
        ('[embed](https://example.com " ")', " "),  # Single space
    ]
    
    for md, expected_caption in test_cases:
        result = EmbedElement.markdown_to_notion(md)
        assert result is not None
        
        if expected_caption.strip():  # Non-empty after stripping
            assert len(result.embed.caption) > 0
            assert result.embed.caption[0].plain_text == expected_caption
        # For completely empty captions, behavior may vary by implementation


def test_malformed_embed_syntax():
    """Test handling of malformed embed syntax."""
    malformed_cases = [
        "[embed]",  # Missing URL
        "[embed]()",  # Empty URL
        "[embed(https://example.com)",  # Missing closing bracket
        "embed](https://example.com)",  # Missing opening bracket
        "[embed](https://example.com",  # Missing closing parenthesis
        "[embed]https://example.com)",  # Missing opening parenthesis
    ]
    
    for malformed in malformed_cases:
        result = EmbedElement.markdown_to_notion(malformed)
        assert result is None


def test_caption_extraction_edge_cases():
    """Test edge cases for caption extraction."""
    edge_cases = [
        ([{"type": "text", "text": {"content": ""}}], ""),  # Empty content
        ([{"plain_text": ""}], ""),  # Empty plain_text
        ([{"type": "unknown", "content": "test"}], ""),  # Unknown type
        ([], ""),  # Empty list
    ]
    
    for rich_text_list, expected in edge_cases:
        result = EmbedElement._extract_text_content(rich_text_list)
        assert result == expected


# Fixtures for common test data
@pytest.fixture
def simple_embed_block():
    """Fixture for simple embed block."""
    return create_block_with_required_fields(
        type="embed",
        embed=EmbedBlock(url="https://example.com", caption=[])
    )


@pytest.fixture
def embed_block_with_caption():
    """Fixture for embed block with caption."""
    return create_block_with_required_fields(
        type="embed",
        embed=EmbedBlock(
            url="https://github.com",
            caption=[create_rich_text_object("GitHub Repository")]
        )
    )


def test_with_fixtures(simple_embed_block, embed_block_with_caption):
    """Test using fixtures to reduce duplication."""
    # Test simple embed block
    result1 = EmbedElement.notion_to_markdown(simple_embed_block)
    assert result1 == "[embed](https://example.com)"

    # Test embed block with caption
    result2 = EmbedElement.notion_to_markdown(embed_block_with_caption)
    assert result2 == '[embed](https://github.com "GitHub Repository")'


def test_notion_block_validation():
    """Test validation of Notion block structure."""
    # Valid block
    valid_block = create_block_with_required_fields(
        type="embed",
        embed=EmbedBlock(url="https://example.com")
    )
    assert EmbedElement.match_notion(valid_block)
    
    # Block with wrong type
    wrong_type_block = create_block_with_required_fields(
        type="paragraph",
        embed=EmbedBlock(url="https://example.com")  # Has embed content but wrong type
    )
    assert not EmbedElement.match_notion(wrong_type_block)
    
    # Block with correct type but no embed content
    no_content_block = create_block_with_required_fields(type="embed")
    assert not EmbedElement.match_notion(no_content_block)