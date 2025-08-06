import pytest
from unittest.mock import Mock
from notionary.blocks.toggleable_heading import ToggleableHeadingElement
from notionary.blocks.heading.heading_models import CreateHeading1Block, CreateHeading2Block, CreateHeading3Block


def test_match_markdown_heading_variants():
    assert ToggleableHeadingElement.match_markdown("+# Foo")
    assert ToggleableHeadingElement.match_markdown("+## Bar") 
    assert ToggleableHeadingElement.match_markdown("+### Baz")
    assert not ToggleableHeadingElement.match_markdown("## Not Toggle")
    assert not ToggleableHeadingElement.match_markdown("+#### Too deep")
    assert not ToggleableHeadingElement.match_markdown("+ Foo")  # Kein Level


@pytest.mark.parametrize(
    "text,level,content",
    [
        ("+# Section 1", 1, "Section 1"),
        ("+## Subsection", 2, "Subsection"),
        ("+### Tief", 3, "Tief"),
    ],
)
def test_markdown_to_notion_basic(text, level, content):
    block = ToggleableHeadingElement.markdown_to_notion(text)
    assert block is not None
    assert block.type == f"heading_{level}"
    
    # Get the heading content based on level
    heading = getattr(block, f"heading_{level}")
    assert heading.is_toggleable is True
    assert heading.color == "default"
    assert isinstance(heading.rich_text, list)
    assert len(heading.rich_text) > 0
    assert heading.rich_text[0].plain_text == content


def test_markdown_to_notion_fail_cases():
    assert ToggleableHeadingElement.markdown_to_notion("## Not toggle") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#### Too deep") is None
    assert ToggleableHeadingElement.markdown_to_notion("") is None


def test_notion_to_markdown_basic():
    # Create a mock Block object
    block = Mock()
    block.type = "heading_2"
    
    # Mock the heading content
    heading_content = Mock()
    heading_content.is_toggleable = True
    heading_content.rich_text = [Mock()]
    heading_content.rich_text[0].plain_text = "Ein Titel"
    
    # Mock the get_block_content method
    block.get_block_content.return_value = heading_content
    
    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result == "+## Ein Titel"


def test_notion_to_markdown_non_toggleable():
    block = Mock()
    block.type = "heading_2"
    
    heading_content = Mock()
    heading_content.is_toggleable = False
    block.get_block_content.return_value = heading_content
    
    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result is None


def test_notion_to_markdown_wrong_type():
    block = Mock()
    block.type = "paragraph"
    
    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result is None


@pytest.mark.parametrize("level", [1, 2, 3])
def test_roundtrip(level):
    content = f"Ein Toggle Level {level}"
    md = f'+{"#"*level} {content}'
    
    # Convert to notion
    block = ToggleableHeadingElement.markdown_to_notion(md)
    assert block is not None
    
    # Create a mock Block for notion_to_markdown
    mock_block = Mock()
    mock_block.type = f"heading_{level}"
    
    # Extract the heading content from the created block
    heading_content = getattr(block, f"heading_{level}")
    mock_block.get_block_content.return_value = heading_content
    
    # Convert back to markdown
    result = ToggleableHeadingElement.notion_to_markdown(mock_block)
    assert result == md


def test_match_notion_toggleable_heading():
    """Test match_notion for toggleable headings."""
    # Mock toggleable heading
    mock_block = Mock()
    mock_block.type = "heading_1"
    mock_heading = Mock()
    mock_heading.is_toggleable = True
    mock_block.get_block_content.return_value = mock_heading
    
    assert ToggleableHeadingElement.match_notion(mock_block)
    
    # Non-toggleable should not match
    mock_heading.is_toggleable = False
    assert not ToggleableHeadingElement.match_notion(mock_block)
    
    # Non-heading should not match
    mock_block.type = "paragraph"
    assert not ToggleableHeadingElement.match_notion(mock_block)


def test_pattern_matching():
    """Test the regex pattern directly."""
    # Valid patterns
    assert ToggleableHeadingElement.PATTERN.match("+# Title")
    assert ToggleableHeadingElement.PATTERN.match("+## Subtitle")
    assert ToggleableHeadingElement.PATTERN.match("+### Section")
    
    # Invalid patterns
    assert not ToggleableHeadingElement.PATTERN.match("# Regular heading")
    assert not ToggleableHeadingElement.PATTERN.match("+#### Too deep")
    assert not ToggleableHeadingElement.PATTERN.match("+ No level")


def test_content_extraction():
    """Test content extraction from markdown."""
    text = "+## My Toggleable Section"
    block = ToggleableHeadingElement.markdown_to_notion(text)
    
    assert block is not None
    heading = block.heading_2
    assert heading.rich_text[0].plain_text == "My Toggleable Section"


def test_empty_content_handling():
    """Test handling of empty content."""
    # Empty content after level should fail
    assert ToggleableHeadingElement.markdown_to_notion("+#") is None
    assert ToggleableHeadingElement.markdown_to_notion("+##   ") is None


def test_whitespace_handling():
    """Test handling of extra whitespace."""
    text = "+#    Title with spaces   "
    block = ToggleableHeadingElement.markdown_to_notion(text)
    
    assert block is not None
    heading = block.heading_1
    # Content should be trimmed
    assert heading.rich_text[0].plain_text == "Title with spaces"


def test_unicode_content():
    """Test Unicode content in toggleable headings."""
    unicode_texts = [
        "+# Überschrift mit Umlauten äöüß",
        "+## 中文标题",
        "+### Заголовок на русском",
        "+# Emoji title 🚀 ✨"
    ]
    
    for text in unicode_texts:
        block = ToggleableHeadingElement.markdown_to_notion(text)
        assert block is not None
        # Just verify it doesn't crash and creates valid content


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = ToggleableHeadingElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, 'syntax')
    assert "+#" in content.syntax
    assert "pipe" in content.syntax.lower()