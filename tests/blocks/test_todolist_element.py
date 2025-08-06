"""
Pytest tests for TodoElement.
Tests conversion between Markdown todos and Notion to_do blocks.
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.todo import TodoElement
from notionary.blocks.todo.todo_models import CreateToDoBlock, ToDoBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


@pytest.mark.parametrize(
    "line,expected",
    [
        ("- [ ] Unchecked todo", True),
        ("* [ ] Unchecked todo", True),
        ("+ [ ] Unchecked todo", True),
        ("  - [ ] Indented todo", True),
        ("- [x] Checked todo", True),
        ("* [x] Checked todo", True),
        ("+ [x] Checked todo", True),
        ("- Regular list item", False),
        ("[ ] Not a todo", False),
        ("- [o] Invalid checkbox", False),
        ("", False),
    ],
)
def test_match_markdown(line, expected):
    assert TodoElement.match_markdown(line) == expected


@pytest.mark.parametrize(
    "block_type,expected",
    [
        ("to_do", True),
        ("paragraph", False),
        ("bulleted_list_item", False),
        ("something_else", False),
    ],
)
def test_match_notion(block_type, expected):
    # Create proper Mock Block object
    block = Mock()
    block.type = block_type
    if block_type == "to_do":
        block.to_do = Mock()  # to_do content exists
    else:
        block.to_do = None
        
    assert TodoElement.match_notion(block) == expected


@pytest.mark.parametrize(
    "md,checked,expected_text",
    [
        ("- [ ] Buy groceries", False, "Buy groceries"),
        ("- [x] Complete assignment", True, "Complete assignment"),
        ("* [ ] Call Mom", False, "Call Mom"),
        ("+ [x] Pay bills", True, "Pay bills"),
        ("  - [ ] Indented", False, "Indented"),
    ],
)
def test_markdown_to_notion(md, checked, expected_text):
    result = TodoElement.markdown_to_notion(md)
    
    assert result is not None
    assert isinstance(result, CreateToDoBlock)
    assert result.type == "to_do"
    assert isinstance(result.to_do, ToDoBlock)
    assert result.to_do.checked == checked
    assert result.to_do.color == "default"
    
    # Check rich text content
    assert len(result.to_do.rich_text) > 0
    extracted = TextInlineFormatter.extract_text_with_formatting(
        [rt.model_dump() for rt in result.to_do.rich_text]
    )
    assert expected_text in extracted


@pytest.mark.parametrize(
    "md",
    ["- Regular list item", "[ ] Not a todo", "- [o] Invalid checkbox", "", "nope"],
)
def test_markdown_to_notion_invalid(md):
    assert TodoElement.markdown_to_notion(md) is None


def test_notion_to_markdown_unchecked():
    # Create a proper mock Block object
    block = Mock()
    block.type = "to_do"
    
    # Create mock to_do content with real RichTextObject
    todo_content = Mock()
    rich_text = RichTextObject.from_plain_text("Buy groceries")
    todo_content.rich_text = [rich_text]
    todo_content.checked = False
    
    block.to_do = todo_content
    
    markdown = TodoElement.notion_to_markdown(block)
    assert markdown == "- [ ] Buy groceries"


def test_notion_to_markdown_checked():
    # Create a proper mock Block object
    block = Mock()
    block.type = "to_do"
    
    # Create mock to_do content with real RichTextObject
    todo_content = Mock()
    rich_text = RichTextObject.from_plain_text("Complete assignment")
    todo_content.rich_text = [rich_text]
    todo_content.checked = True
    
    block.to_do = todo_content
    
    markdown = TodoElement.notion_to_markdown(block)
    assert markdown == "- [x] Complete assignment"


def test_notion_to_markdown_invalid():
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.to_do = None
    assert TodoElement.notion_to_markdown(paragraph_block) is None
    
    # No to_do content
    todo_block = Mock()
    todo_block.type = "to_do"
    todo_block.to_do = None
    assert TodoElement.notion_to_markdown(todo_block) is None


def test_with_formatting():
    todo_with_formatting = "- [ ] Remember to *buy* **groceries**"
    notion_result = TodoElement.markdown_to_notion(todo_with_formatting)
    
    assert notion_result is not None
    
    # Create mock Block for notion_to_markdown
    mock_block = Mock()
    mock_block.type = "to_do"
    mock_block.to_do = notion_result.to_do
    
    markdown = TodoElement.notion_to_markdown(mock_block)
    
    # Should contain the formatted text and keep the todo structure
    assert "Remember to" in markdown
    assert "*buy*" in markdown  # Formatting should be preserved
    assert "**groceries**" in markdown  # Formatting should be preserved
    assert markdown.startswith("- [ ] ")


# REMOVED: test_is_multiline - method doesn't exist anymore


@pytest.mark.parametrize(
    "md",
    [
        "- [ ] Käse kaufen",
        "- [x] Aufgabe erledigt 🙂",
        "* [x] Mit Unicode äöüß",
        "+ [ ] Todo mit Emoji 👍",
    ],
)
def test_unicode_content(md):
    result = TodoElement.markdown_to_notion(md)
    assert result is not None
    
    text = TextInlineFormatter.extract_text_with_formatting(
        [rt.model_dump() for rt in result.to_do.rich_text]
    )
    
    # Check that unicode content is preserved
    for word in md.split():
        if word not in ["- [ ]", "[x]", "*", "+"]:
            # Clean up the word and check if meaningful content is preserved
            clean_word = word.strip("[]()+-*x")
            if clean_word and len(clean_word) > 1:
                assert any(c in text for c in clean_word if c.isalnum() or ord(c) > 127)


def test_roundtrip():
    cases = [
        "- [ ] Do homework",
        "- [x] Submit report", 
        "* [ ] Walk the dog",
        "+ [x] Finish project",
        "- [ ] 🥦 Gemüse kaufen",
        "- [x] Aufgabe erledigt 🙂",
    ]
    for md in cases:
        # Convert to notion
        notion_result = TodoElement.markdown_to_notion(md)
        assert notion_result is not None
        
        # Create proper mock Block for notion_to_markdown  
        mock_block = Mock()
        mock_block.type = "to_do"
        mock_block.to_do = notion_result.to_do
        
        # Convert back to markdown
        back = TodoElement.notion_to_markdown(mock_block)
        assert back is not None
        
        # The checkbox state and text must be preserved
        if "[x]" in md:
            assert back.startswith("- [x]")
        else:
            assert back.startswith("- [ ]")
            
        # Extract the main content (after the checkbox)
        original_content = md.split("] ", 1)[1] if "] " in md else md[6:]
        back_content = back.split("] ", 1)[1] if "] " in back else back[6:]
        
        # Check that meaningful words are preserved
        original_words = [w.strip() for w in original_content.split() if w.strip()]
        back_words = [w.strip() for w in back_content.split() if w.strip()]
        
        for word in original_words:
            # For emoji and unicode, just check that some form is preserved
            if any(ord(c) > 127 for c in word):  # Unicode/Emoji
                assert any(word in back_word or back_word in word for back_word in back_words)
            else:  # Regular words
                assert word in back_words


def test_pattern_matching():
    """Test the regex patterns directly."""
    # Test PATTERN (unchecked)
    assert TodoElement.PATTERN.match("- [ ] Test")
    assert TodoElement.PATTERN.match("* [ ] Test")  
    assert TodoElement.PATTERN.match("+ [ ] Test")
    assert TodoElement.PATTERN.match("  - [ ] Indented")
    
    # Test DONE_PATTERN (checked)
    assert TodoElement.DONE_PATTERN.match("- [x] Done")
    assert TodoElement.DONE_PATTERN.match("* [X] Done")  # Case insensitive
    assert TodoElement.DONE_PATTERN.match("+ [x] Done")
    
    # Invalid patterns
    assert not TodoElement.PATTERN.match("- Regular list")
    assert not TodoElement.DONE_PATTERN.match("- [ ] Not done")


def test_checkbox_state_detection():
    """Test that checkbox state is correctly detected."""
    unchecked_cases = [
        "- [ ] Task 1",
        "* [ ] Task 2", 
        "+ [ ] Task 3"
    ]
    
    checked_cases = [
        "- [x] Done 1",
        "* [X] Done 2",  # Capital X should work  
        "+ [x] Done 3"
    ]
    
    for md in unchecked_cases:
        result = TodoElement.markdown_to_notion(md)
        assert result is not None
        assert result.to_do.checked is False
    
    for md in checked_cases:
        result = TodoElement.markdown_to_notion(md)
        assert result is not None
        assert result.to_do.checked is True


def test_empty_todo_content():
    """Test handling of todos with empty content."""
    # These should still work but with empty content
    empty_cases = [
        "- [ ] ",
        "* [x] ",
    ]
    
    for md in empty_cases:
        # Depending on implementation, this might return None or empty content
        # Let's test the actual behavior
        result = TodoElement.markdown_to_notion(md)
        if result is not None:
            # If it succeeds, the content should be empty or minimal
            text = TextInlineFormatter.extract_text_with_formatting(
                [rt.model_dump() for rt in result.to_do.rich_text]
            )
            assert len(text.strip()) == 0


def test_whitespace_handling():
    """Test handling of extra whitespace."""
    md = "  - [ ]   Task with spaces   "
    result = TodoElement.markdown_to_notion(md)
    
    assert result is not None
    text = TextInlineFormatter.extract_text_with_formatting(
        [rt.model_dump() for rt in result.to_do.rich_text]  
    )
    assert "Task with spaces" in text


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = TodoElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, 'syntax')
    assert "[ ]" in content.syntax
    assert "[x]" in content.syntax or "checkbox" in content.syntax.lower()