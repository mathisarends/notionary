"""
Pytest tests for HeadingElement.
Tests conversion between Markdown headings and Notion heading blocks.
"""

import pytest
from notionary.blocks import HeadingElement


def test_match_markdown_valid_headings():
    """Test recognition of valid Markdown heading formats."""
    assert HeadingElement.match_markdown("# Heading 1")
    assert HeadingElement.match_markdown("## Heading 2")
    assert HeadingElement.match_markdown("### Heading 3")
    assert HeadingElement.match_markdown("# Simple")
    assert HeadingElement.match_markdown("### With **bold** text")


def test_match_markdown_invalid_formats():
    """Test rejection of invalid heading formats."""
    assert not HeadingElement.match_markdown("#### Heading 4")  # Level 4 not supported
    assert not HeadingElement.match_markdown("##### Heading 5")  # Level 5 not supported
    assert not HeadingElement.match_markdown(
        "###### Heading 6"
    )  # Level 6 not supported
    assert not HeadingElement.match_markdown("####### Too many hashes")
    assert not HeadingElement.match_markdown("No heading here")
    assert not HeadingElement.match_markdown("#")  # Missing content
    assert not HeadingElement.match_markdown("# ")  # Only space after hash
    assert not HeadingElement.match_markdown("")  # Empty string


def test_match_notion():
    """Test recognition of Notion heading blocks."""
    assert HeadingElement.match_notion({"type": "heading_1"})
    assert HeadingElement.match_notion({"type": "heading_2"})
    assert HeadingElement.match_notion({"type": "heading_3"})

    assert not HeadingElement.match_notion({"type": "paragraph"})
    assert not HeadingElement.match_notion({"type": "heading_4"})  # Not supported
    assert not HeadingElement.match_notion({"type": "heading_7"})
    assert not HeadingElement.match_notion({"type": "heading_"})  # Invalid format
    assert not HeadingElement.match_notion({})  # Empty dict


def test_markdown_to_notion_level_1():
    """Test conversion of H1 heading to Notion."""
    result = HeadingElement.markdown_to_notion("# Main Title")

    assert result is not None
    assert isinstance(result, list)

    heading_block = result[0]
    assert heading_block["type"] == "heading_1"
    assert heading_block["heading_1"]["rich_text"][0]["type"] == "text"
    assert heading_block["heading_1"]["rich_text"][0]["text"]["content"] == "Main Title"


def test_markdown_to_notion_level_2():
    """Test conversion of H2 heading to Notion."""
    result = HeadingElement.markdown_to_notion("## Subtitle")

    heading_block = result[0]
    assert heading_block["type"] == "heading_2"
    assert heading_block["heading_2"]["rich_text"][0]["text"]["content"] == "Subtitle"


def test_markdown_to_notion_level_3():
    """Test conversion of H3 heading to Notion."""
    result = HeadingElement.markdown_to_notion("### Section")

    heading_block = result[0]
    assert heading_block["type"] == "heading_3"
    assert heading_block["heading_3"]["rich_text"][0]["text"]["content"] == "Section"


def test_markdown_to_notion_invalid():
    """Test that invalid Markdown returns None."""
    assert HeadingElement.markdown_to_notion("Just a paragraph") is None
    assert HeadingElement.markdown_to_notion("#### Level 4") is None  # Not supported
    assert HeadingElement.markdown_to_notion("#") is None  # Missing content
    assert HeadingElement.markdown_to_notion("") is None


def test_notion_to_markdown_level_1():
    """Test conversion of Notion H1 to Markdown."""
    block = {
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": "Main Title"}}]
        },
    }

    result = HeadingElement.notion_to_markdown(block)
    assert result == "# Main Title"


def test_notion_to_markdown_level_2():
    """Test conversion of Notion H2 to Markdown."""
    block = {
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Subtitle"}}]},
    }

    result = HeadingElement.notion_to_markdown(block)
    assert result == "## Subtitle"


def test_notion_to_markdown_level_3():
    """Test conversion of Notion H3 to Markdown."""
    block = {
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{"type": "text", "text": {"content": "Section Title"}}]
        },
    }

    result = HeadingElement.notion_to_markdown(block)
    assert result == "### Section Title"


def test_notion_to_markdown_invalid():
    """Test that invalid Notion blocks return None."""
    assert HeadingElement.notion_to_markdown({"type": "paragraph"}) is None
    assert HeadingElement.notion_to_markdown({"type": "heading_x"}) is None
    assert (
        HeadingElement.notion_to_markdown({"type": "heading_4"}) is None
    )  # Not supported
    assert HeadingElement.notion_to_markdown({}) is None


def test_heading_with_inline_formatting():
    """Test headings with inline formatting like bold and italic."""
    markdown = "### This is **important** and *emphasized*"

    result = HeadingElement.markdown_to_notion(markdown)
    assert result is not None

    heading_block = result[0]
    assert heading_block["type"] == "heading_3"

    # Should have multiple rich_text segments for formatting
    rich_text = heading_block["heading_3"]["rich_text"]
    assert len(rich_text) > 1  # Multiple segments due to formatting

    # Convert back to markdown
    back_to_markdown = HeadingElement.notion_to_markdown(heading_block)
    assert back_to_markdown.startswith("###")
    assert "important" in back_to_markdown
    assert "emphasized" in back_to_markdown


def test_is_multiline():
    """Test that headings are recognized as single-line elements."""
    assert not HeadingElement.is_multiline()


def test_roundtrip_conversion():
    """Test that Markdown -> Notion -> Markdown preserves content."""
    test_cases = [
        "# Main Title",
        "## Subtitle with Content",
        "### Section Header",
    ]

    for original_markdown in test_cases:
        # Convert to Notion
        notion_result = HeadingElement.markdown_to_notion(original_markdown)
        assert notion_result is not None

        # Convert back to Markdown
        markdown_result = HeadingElement.notion_to_markdown(notion_result[0])
        assert markdown_result == original_markdown


# Parametrized tests for different heading levels
@pytest.mark.parametrize(
    "level,content,expected_type",
    [
        (1, "Title", "heading_1"),
        (2, "Subtitle", "heading_2"),
        (3, "Section", "heading_3"),
    ],
)
def test_heading_levels(level, content, expected_type):
    """Test different heading levels conversion."""
    markdown = "#" * level + f" {content}"

    result = HeadingElement.markdown_to_notion(markdown)
    assert result is not None

    heading_block = result[0]
    assert heading_block["type"] == expected_type
    assert heading_block[expected_type]["rich_text"][0]["text"]["content"] == content


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("# Valid H1", True),
        ("## Valid H2", True),
        ("### Valid H3", True),
        ("#### Invalid H4", False),
        ("##### Invalid H5", False),
        ("###### Invalid H6", False),
        ("####### Too many", False),
        ("Not a heading", False),
        ("#", False),  # Missing content
        ("# ", False),  # Only space
        ("", False),  # Empty
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various Markdown patterns."""
    result = HeadingElement.match_markdown(markdown)
    assert result == should_match


@pytest.mark.parametrize(
    "block_type,should_match",
    [
        ("heading_1", True),
        ("heading_2", True),
        ("heading_3", True),
        ("heading_4", False),  # Not supported
        ("heading_5", False),  # Not supported
        ("paragraph", False),
        ("callout", False),
        ("quote", False),
    ],
)
def test_notion_block_recognition(block_type, should_match):
    """Test recognition of different Notion block types."""
    block = {"type": block_type}
    result = HeadingElement.match_notion(block)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def h1_block():
    """Fixture for H1 Notion block."""
    return {
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": "Main Title"}}]
        },
    }


@pytest.fixture
def h2_block():
    """Fixture for H2 Notion block."""
    return {
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Subtitle"}}]},
    }


@pytest.fixture
def h3_block():
    """Fixture for H3 Notion block."""
    return {
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": "Section"}}]},
    }


def test_with_fixtures(h1_block, h2_block, h3_block):
    """Test using fixtures to reduce duplication."""
    # Test H1
    result1 = HeadingElement.notion_to_markdown(h1_block)
    assert result1 == "# Main Title"

    # Test H2
    result2 = HeadingElement.notion_to_markdown(h2_block)
    assert result2 == "## Subtitle"

    # Test H3
    result3 = HeadingElement.notion_to_markdown(h3_block)
    assert result3 == "### Section"


def test_empty_heading_content():
    """Test handling of headings with empty or whitespace content."""
    # This should be invalid
    assert not HeadingElement.match_markdown("# ")
    assert not HeadingElement.match_markdown("##  ")
    assert not HeadingElement.match_markdown("###\t")


def test_heading_with_special_characters():
    """Test headings containing special characters."""
    special_cases = [
        "# Title with (parentheses)",
        "## Title with [brackets]",
        "### Title with *asterisks*",
        "# Title with `code`",
        "## Title with @mentions",
        "### Title with #hashtags",
    ]

    for markdown in special_cases:
        result = HeadingElement.markdown_to_notion(markdown)
        assert result is not None, f"Failed to convert: {markdown}"

        # Should be able to convert back
        heading_block = result[0]
        back_to_markdown = HeadingElement.notion_to_markdown(heading_block)
        assert back_to_markdown is not None


def test_notion_block_structure():
    """Test the exact structure of converted Notion blocks."""
    result = HeadingElement.markdown_to_notion("## Test Heading")

    assert isinstance(result, list)
    assert len(result) == 1  # Only the heading block

    heading_block = result[0]
    assert heading_block["type"] == "heading_2"
    assert "heading_2" in heading_block
    assert "rich_text" in heading_block["heading_2"]
    assert isinstance(heading_block["heading_2"]["rich_text"], list)
    assert len(heading_block["heading_2"]["rich_text"]) >= 1


def test_rich_text_structure():
    """Test the structure of rich_text in converted blocks."""
    result = HeadingElement.markdown_to_notion("# Simple Heading")

    heading_block = result[0]
    rich_text = heading_block["heading_1"]["rich_text"]

    # First segment should be plain text
    first_segment = rich_text[0]
    assert first_segment["type"] == "text"
    assert "text" in first_segment
    assert "content" in first_segment["text"]
    assert first_segment["text"]["content"] == "Simple Heading"


def test_level_validation():
    """Test that only levels 1-3 are supported."""
    valid_levels = [1, 2, 3]
    invalid_levels = [0, 4, 5, 6, 7, 8, 9, 10]

    # Valid levels should work
    for level in valid_levels:
        markdown = "#" * level + " Test"
        assert HeadingElement.match_markdown(markdown), f"Level {level} should be valid"

    # Invalid levels should not work
    for level in invalid_levels:
        if level > 0:  # Skip level 0 as it would be empty string
            markdown = "#" * level + " Test"
            assert (
                not HeadingElement.match_markdown()
            ), f"Level {level} should be invalid"


def test_whitespace_handling():
    """Test proper handling of whitespace in headings."""
    # Should work with various whitespace after hash
    valid_cases = [
        "# Title",  # Single space
        "#  Title",  # Multiple spaces
        "#\tTitle",  # Tab
    ]

    for case in valid_cases:
        assert HeadingElement.match_markdown(case), f"Should match: '{case}'"

    # Should preserve content after whitespace normalization
    result = HeadingElement.markdown_to_notion("#  Multiple   Spaces")
    heading_block = result[0]
    content = heading_block["heading_1"]["rich_text"][0]["text"]["content"]
    assert content == "Multiple   Spaces"  # Internal spaces preserved


def test_unicode_content():
    """Test headings with Unicode characters."""
    unicode_cases = [
        "# Überschrift mit Umlauten",
        "## 标题 with Chinese",
        "### Título en Español",
        "# 🎉 Heading with Emoji",
        "## αβγ Greek Letters",
    ]

    for markdown in unicode_cases:
        result = HeadingElement.markdown_to_notion(markdown)
        assert result is not None, f"Failed with Unicode: {markdown}"

        # Should convert back properly
        heading_block = result[0]
        back_to_markdown = HeadingElement.notion_to_markdown(heading_block)
        assert back_to_markdown is not None
