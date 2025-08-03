"""
Pytest tests for DividerElement.
Tests conversion between Markdown horizontal dividers and Notion divider blocks.
"""

import pytest
from notionary.blocks.divider import DividerElement
from notionary.blocks.divider.divider_models import DividerBlock, CreateDividerBlock
from notionary.blocks.paragraph.paragraph_models import (
    ParagraphBlock,
    CreateParagraphBlock,
)
from notionary.blocks.block_models import Block


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"},
    }
    defaults.update(kwargs)
    return Block(**defaults)


def test_match_markdown_valid_dividers():
    """Test recognition of valid Markdown divider formats."""
    assert DividerElement.match_markdown("---")
    assert DividerElement.match_markdown("----")
    assert DividerElement.match_markdown("-----")
    assert DividerElement.match_markdown("   ---   ")  # With whitespace
    assert DividerElement.match_markdown("\t---\t")  # With tabs


def test_match_markdown_invalid_formats():
    """Test rejection of invalid divider formats."""
    assert not DividerElement.match_markdown("- - -")  # Spaced dashes
    assert not DividerElement.match_markdown("--")  # Too short
    assert not DividerElement.match_markdown("text---text")  # Text around
    assert not DividerElement.match_markdown("---text")  # Text after
    assert not DividerElement.match_markdown("text---")  # Text before
    assert not DividerElement.match_markdown("***")  # Wrong character
    assert not DividerElement.match_markdown("___")  # Wrong character
    assert not DividerElement.match_markdown("")  # Empty string


def test_match_notion():
    """Test recognition of Notion divider blocks."""
    divider_block = create_block_with_required_fields(
        type="divider", divider=DividerBlock()
    )
    assert DividerElement.match_notion(divider_block)

    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert not DividerElement.match_notion(paragraph_block)

    heading_block = create_block_with_required_fields(type="heading_1")
    assert not DividerElement.match_notion(heading_block)

    code_block = create_block_with_required_fields(type="code")
    assert not DividerElement.match_notion(code_block)


def test_markdown_to_notion_valid():
    """Test conversion of valid Markdown dividers to Notion format."""
    result = DividerElement.markdown_to_notion("---")

    assert isinstance(result, list)
    assert len(result) == 2

    # First element: empty paragraph
    empty_paragraph = result[0]
    assert isinstance(empty_paragraph, CreateParagraphBlock)
    assert empty_paragraph.type == "paragraph"
    assert empty_paragraph.paragraph.rich_text == []

    # Second element: divider
    divider = result[1]
    assert isinstance(divider, CreateDividerBlock)
    assert divider.type == "divider"
    assert isinstance(divider.divider, DividerBlock)

    # Test other valid formats
    result2 = DividerElement.markdown_to_notion("----")
    assert result2 is not None
    assert len(result2) == 2

    result3 = DividerElement.markdown_to_notion("  -----  ")
    assert result3 is not None
    assert len(result3) == 2


def test_markdown_to_notion_invalid():
    """Test that invalid Markdown returns None."""
    assert DividerElement.markdown_to_notion("not a divider") is None
    assert DividerElement.markdown_to_notion("--") is None
    assert DividerElement.markdown_to_notion("- - -") is None
    assert DividerElement.markdown_to_notion("") is None


def test_notion_to_markdown():
    """Test conversion from Notion divider block to Markdown."""
    # Valid divider block
    divider_block = create_block_with_required_fields(
        type="divider", divider=DividerBlock()
    )
    assert DividerElement.notion_to_markdown(divider_block) == "---"

    # Divider block with extra properties (should still work)
    divider_with_extra = create_block_with_required_fields(
        type="divider", divider=DividerBlock(), archived=False, has_children=False
    )
    assert DividerElement.notion_to_markdown(divider_with_extra) == "---"


def test_notion_to_markdown_invalid():
    """Test that invalid Notion blocks return None."""
    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert DividerElement.notion_to_markdown(paragraph_block) is None

    heading_block = create_block_with_required_fields(type="heading_1")
    assert DividerElement.notion_to_markdown(heading_block) is None

    # Block without divider content
    invalid_divider = create_block_with_required_fields(type="divider")
    assert DividerElement.notion_to_markdown(invalid_divider) is None


def test_is_multiline():
    """Test that dividers are recognized as single-line elements."""
    assert not DividerElement.is_multiline()


def test_roundtrip_conversion():
    """Test that Markdown -> Notion -> Markdown preserves the divider."""
    original_markdown = "---"

    # Convert to Notion
    notion_blocks = DividerElement.markdown_to_notion(original_markdown)
    assert notion_blocks is not None

    # Extract the divider block (second element after empty paragraph)
    divider_create_block = notion_blocks[1]
    assert isinstance(divider_create_block, CreateDividerBlock)
    assert divider_create_block.type == "divider"

    # Create a Block for notion_to_markdown
    divider_block = create_block_with_required_fields(
        type="divider", divider=divider_create_block.divider
    )

    # Convert back to Markdown
    result_markdown = DividerElement.notion_to_markdown(divider_block)
    assert result_markdown == original_markdown


# Parametrized tests for various divider formats
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("---", True),
        ("----", True),
        ("-----", True),
        ("------", True),
        ("   ---   ", True),
        ("\t---\t", True),
        ("--", False),
        ("- - -", False),
        ("***", False),
        ("___", False),
        ("text---", False),
        ("---text", False),
        ("text---text", False),
        ("", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various Markdown patterns."""
    result = DividerElement.match_markdown(markdown)
    assert result == should_match


@pytest.mark.parametrize(
    "block_type,should_match",
    [
        ("divider", True),
        ("paragraph", False),
        ("heading_1", False),
        ("heading_2", False),
        ("code", False),
        ("callout", False),
        ("quote", False),
    ],
)
def test_notion_block_recognition(block_type, should_match):
    """Test recognition of different Notion block types."""
    block_data = {"type": block_type}

    if block_type == "divider":
        block_data["divider"] = DividerBlock()

    block = create_block_with_required_fields(**block_data)
    result = DividerElement.match_notion(block)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def valid_divider_block():
    """Fixture for valid Notion divider block."""
    return create_block_with_required_fields(type="divider", divider=DividerBlock())


@pytest.fixture
def invalid_divider_block():
    """Fixture for invalid Notion block."""
    return create_block_with_required_fields(
        type="paragraph", paragraph=ParagraphBlock(rich_text=[])
    )


def test_with_fixtures(valid_divider_block, invalid_divider_block):
    """Test using fixtures to reduce duplication."""
    # Test valid divider block
    result1 = DividerElement.notion_to_markdown(valid_divider_block)
    assert result1 == "---"

    # Test invalid block
    result2 = DividerElement.notion_to_markdown(invalid_divider_block)
    assert result2 is None


def test_whitespace_handling():
    """Test proper handling of whitespace in divider detection."""
    whitespace_cases = [
        "   ---   ",  # Spaces around
        "\t---\t",  # Tabs around
        " \t ---\t ",  # Mixed whitespace
        "---   ",  # Trailing whitespace
        "   ---",  # Leading whitespace
    ]

    for case in whitespace_cases:
        assert DividerElement.match_markdown(case), f"Failed for: '{case}'"

        # Should also convert properly
        result = DividerElement.markdown_to_notion(case)
        assert result is not None
        assert isinstance(result[1], CreateDividerBlock)
        assert result[1].type == "divider"


def test_minimum_dash_count():
    """Test that minimum of 3 dashes is required."""
    # Valid cases (3 or more dashes)
    valid_cases = ["---", "----", "-----", "------"]
    for case in valid_cases:
        assert DividerElement.match_markdown(case), f"Should match: {case}"

    # Invalid cases (less than 3 dashes)
    invalid_cases = ["-", "--"]
    for case in invalid_cases:
        assert not DividerElement.match_markdown(case), f"Should not match: {case}"


def test_notion_block_structure():
    """Test the exact structure of converted Notion blocks."""
    result = DividerElement.markdown_to_notion("---")

    # Should return array with empty paragraph + divider
    assert isinstance(result, list)
    assert len(result) == 2

    # First element: empty paragraph
    empty_paragraph = result[0]
    assert isinstance(empty_paragraph, CreateParagraphBlock)
    assert empty_paragraph.type == "paragraph"
    assert empty_paragraph.paragraph.rich_text == []

    # Second element: divider
    divider = result[1]
    assert isinstance(divider, CreateDividerBlock)
    assert divider.type == "divider"
    assert isinstance(divider.divider, DividerBlock)


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Very long divider
    long_divider = "-" * 100
    assert DividerElement.match_markdown(long_divider)

    # Divider with maximum reasonable whitespace
    padded_divider = " " * 10 + "---" + " " * 10
    assert DividerElement.match_markdown(padded_divider)

    # Mixed with other characters should fail
    mixed_cases = [
        "---abc",
        "abc---",
        "a---b",
        "- --",
        "-- -",
    ]

    for case in mixed_cases:
        assert not DividerElement.match_markdown(case), f"Should not match: {case}"


def test_notion_properties_ignored():
    """Test that extra properties in Notion blocks are ignored."""
    divider_with_extra = create_block_with_required_fields(
        type="divider",
        divider=DividerBlock(),
        archived=False,
        has_children=False,
        in_trash=False,
    )

    # Should still convert properly despite extra properties
    result = DividerElement.notion_to_markdown(divider_with_extra)
    assert result == "---"


def test_consistency():
    """Test consistency of conversion methods."""
    test_cases = ["---", "----", "-----"]

    for original in test_cases:
        # Convert to Notion
        notion_result = DividerElement.markdown_to_notion(original)
        assert notion_result is not None

        # Extract divider block
        divider_create_block = notion_result[1]  # Skip empty paragraph
        assert isinstance(divider_create_block, CreateDividerBlock)

        # Create Block for notion_to_markdown
        divider_block = create_block_with_required_fields(
            type="divider", divider=divider_create_block.divider
        )

        # Convert back to Markdown
        markdown_result = DividerElement.notion_to_markdown(divider_block)

        # Should always return standard "---" format
        assert markdown_result == "---"


def test_empty_paragraph_creation():
    """Test that empty paragraph is created correctly."""
    result = DividerElement.markdown_to_notion("---")

    empty_paragraph = result[0]
    assert isinstance(empty_paragraph, CreateParagraphBlock)
    assert empty_paragraph.type == "paragraph"
    assert isinstance(empty_paragraph.paragraph, ParagraphBlock)
    assert empty_paragraph.paragraph.rich_text == []
    assert empty_paragraph.paragraph.color == "default"


def test_divider_block_creation():
    """Test that divider block is created correctly."""
    result = DividerElement.markdown_to_notion("---")

    divider = result[1]
    assert isinstance(divider, CreateDividerBlock)
    assert divider.type == "divider"
    assert isinstance(divider.divider, DividerBlock)


def test_pattern_matching_edge_cases():
    """Test edge cases for pattern matching."""
    # Test with various whitespace combinations
    edge_cases = [
        ("   ---", True),  # Leading spaces
        ("---   ", True),  # Trailing spaces
        ("\t---", True),  # Leading tab
        ("---\t", True),  # Trailing tab
        (" \t---\t ", True),  # Mixed whitespace
        ("", False),  # Empty string
        ("   ", False),  # Only whitespace
        ("\t\t", False),  # Only tabs
    ]

    for markdown, should_match in edge_cases:
        result = DividerElement.match_markdown(markdown)
        assert result == should_match, f"Failed for '{repr(markdown)}'"


def test_multiple_consecutive_dividers():
    """Test handling of multiple consecutive dividers."""
    dividers = ["---", "----", "-----"]

    for divider in dividers:
        result = DividerElement.markdown_to_notion(divider)
        assert result is not None
        assert len(result) == 2  # Always paragraph + divider

        # All should produce the same structure
        assert isinstance(result[0], CreateParagraphBlock)
        assert isinstance(result[1], CreateDividerBlock)


def test_notion_block_validation():
    """Test validation of Notion block structure."""
    # Valid block
    valid_block = create_block_with_required_fields(
        type="divider", divider=DividerBlock()
    )
    assert DividerElement.match_notion(valid_block)

    # Block with wrong type
    wrong_type_block = create_block_with_required_fields(
        type="paragraph", divider=DividerBlock()  # Has divider content but wrong type
    )
    assert not DividerElement.match_notion(wrong_type_block)

    # Block with correct type but no divider content
    no_content_block = create_block_with_required_fields(type="divider")
    assert not DividerElement.match_notion(no_content_block)
