"""
Pytest tests for CodeElement.
Tests conversion between Markdown code blocks and Notion code blocks.
"""

import pytest
from notionary.blocks import CodeElement


def test_match_markdown_valid_code_blocks():
    """Test recognition of valid Markdown code block syntax."""
    assert CodeElement.match_markdown("```python\nprint('Hello')\n```")
    assert CodeElement.match_markdown("```js\nconsole.log('hi');\n```")
    assert CodeElement.match_markdown("```\nsome code\n```")
    assert CodeElement.match_markdown("```bash\necho 'test'\n```\nCaption: Example")


def test_match_markdown_invalid_formats():
    """Test rejection of invalid formats."""
    assert not CodeElement.match_markdown("This is just text.")
    assert not CodeElement.match_markdown("`inline code`")
    assert not CodeElement.match_markdown("```")  # Incomplete
    assert not CodeElement.match_markdown("```python")  # No closing


def test_match_notion():
    """Test recognition of Notion code blocks.""" 
    assert CodeElement.match_notion({"type": "code"})
    
    assert not CodeElement.match_notion({"type": "paragraph"})
    assert not CodeElement.match_notion({"type": "callout"})


def test_markdown_to_notion_with_language():
    """Test conversion of code block with language specification."""
    result = CodeElement.markdown_to_notion("```python\nprint('Hello')\n```")
    
    assert len(result) == 2  # Code block + empty paragraph
    code_block = result[0]
    
    assert code_block["type"] == "code"
    assert code_block["code"]["language"] == "python"
    assert code_block["code"]["rich_text"][0]["text"]["content"] == "print('Hello')"


def test_markdown_to_notion_without_language():
    """Test conversion of code block without language specification."""
    result = CodeElement.markdown_to_notion("```\njust some code\n```")
    
    code_block = result[0]
    assert code_block["code"]["language"] == "plain text"
    assert code_block["code"]["rich_text"][0]["text"]["content"] == "just some code"


def test_markdown_to_notion_with_caption():
    """Test conversion of code block with caption."""
    markdown = "```python\nprint('test')\n```\nCaption: Example code"
    result = CodeElement.markdown_to_notion(markdown)
    
    code_block = result[0]
    assert code_block["type"] == "code"
    assert "caption" in code_block["code"]
    assert code_block["code"]["caption"][0]["text"]["content"] == "Example code"


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = CodeElement.markdown_to_notion("This is just text.")
    assert result is None


def test_notion_to_markdown():
    """Test conversion of Notion code block to Markdown."""
    block = {
        "type": "code",
        "code": {
            "language": "python",
            "rich_text": [
                {
                    "plain_text": "print('Hi')",
                    "type": "text",
                    "text": {"content": "print('Hi')"},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                }
            ],
        },
    }
    
    result = CodeElement.notion_to_markdown(block)
    assert result == "```python\nprint('Hi')\n```"


def test_notion_to_markdown_with_caption():
    """Test conversion of Notion code block with caption."""
    block = {
        "type": "code",
        "code": {
            "language": "python",
            "rich_text": [{"type": "text", "text": {"content": "print('test')"}}],
            "caption": [{"type": "text", "text": {"content": "Example"}}],
        },
    }
    
    result = CodeElement.notion_to_markdown(block)
    assert result == "```python\nprint('test')\n```\nCaption: Example"


def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    result = CodeElement.notion_to_markdown({"type": "paragraph"})
    assert result is None


def test_find_matches_multiple_blocks():
    """Test extraction of multiple code blocks from text."""
    text = (
        "Intro\n\n"
        "```python\n"
        "print('Hello')\n"
        "```\n\n"
        "Some more text\n\n"
        "```js\n"
        "console.log('Hi');\n"
        "```"
    )
    
    matches = CodeElement.find_matches(text)
    
    assert len(matches) == 2
    
    # Check first match
    first_match = matches[0][2]  # (start, end, block)
    assert first_match["type"] == "code"
    assert first_match["code"]["language"] == "python"
    assert "print('Hello')" in first_match["code"]["rich_text"][0]["text"]["content"]
    
    # Check second match
    second_match = matches[1][2]
    assert second_match["type"] == "code"
    assert second_match["code"]["language"] == "js"
    assert "console.log('Hi');" in second_match["code"]["rich_text"][0]["text"]["content"]


def test_find_matches_empty_text():
    """Test find_matches with empty or no code blocks."""
    # Empty text
    assert CodeElement.find_matches("") == []
    
    # Text without code blocks
    assert CodeElement.find_matches("Just regular text here.") == []


def test_is_multiline():
    """Test that code blocks are recognized as multiline elements."""
    assert CodeElement.is_multiline()


# Parametrized tests for different programming languages
@pytest.mark.parametrize("language,code,expected_lang", [
    ("python", "print('hello')", "python"),
    ("javascript", "console.log('test');", "javascript"),
    ("bash", "echo 'hello'", "bash"),
    ("json", '{"key": "value"}', "json"),
    ("", "plain code", "plain text"),  # No language specified
])
def test_language_support(language, code, expected_lang):
    """Test support for different programming languages."""
    if language:
        markdown = f"```{language}\n{code}\n```"
    else:
        markdown = f"```\n{code}\n```"
    
    result = CodeElement.markdown_to_notion(markdown)
    
    assert result is not None
    code_block = result[0]
    assert code_block["code"]["language"] == expected_lang
    assert code_block["code"]["rich_text"][0]["text"]["content"] == code


@pytest.mark.parametrize("markdown,should_match", [
    ("```python\ncode\n```", True),
    ("```\ncode\n```", True),
    ("```js\ncode\n```\nCaption: test", True),
    ("`inline code`", False),
    ("Regular text", False),
    ("```incomplete", False),
])
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various Markdown patterns."""
    result = CodeElement.match_markdown(markdown)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def simple_code_block():
    """Fixture for simple Notion code block."""
    return {
        "type": "code",
        "code": {
            "language": "python",
            "rich_text": [{"type": "text", "text": {"content": "print('test')"}}],
        },
    }


@pytest.fixture
def code_block_with_caption():
    """Fixture for Notion code block with caption."""
    return {
        "type": "code",
        "code": {
            "language": "javascript",
            "rich_text": [{"type": "text", "text": {"content": "console.log('hello');"}}],
            "caption": [{"type": "text", "text": {"content": "Example JS code"}}],
        },
    }


def test_with_fixtures(simple_code_block, code_block_with_caption):
    """Test using fixtures to reduce duplication."""
    # Test simple code block
    result1 = CodeElement.notion_to_markdown(simple_code_block)
    assert result1 == "```python\nprint('test')\n```"
    
    # Test code block with caption
    result2 = CodeElement.notion_to_markdown(code_block_with_caption)
    assert result2 == "```javascript\nconsole.log('hello');\n```\nCaption: Example JS code"


def test_content_preservation():
    """Test that code content is preserved exactly during conversion."""
    test_cases = [
        "print('hello world')",
        "function test() {\n  return 42;\n}",
        "# Comment\necho 'test'",
        "SELECT * FROM users;",
        '{"name": "test", "value": 123}',
    ]
    
    for code_content in test_cases:
        markdown = f"```\n{code_content}\n```"
        
        # Convert to Notion
        notion_result = CodeElement.markdown_to_notion(markdown)
        assert notion_result is not None
        
        # Check content is preserved
        actual_content = notion_result[0]["code"]["rich_text"][0]["text"]["content"]
        assert actual_content == code_content


def test_trailing_newline_handling():
    """Test proper handling of trailing newlines in code content."""
    # Code with trailing newline
    markdown_with_newline = "```python\nprint('test')\n\n```"
    result = CodeElement.markdown_to_notion(markdown_with_newline)
    
    # Should strip trailing newline
    content = result[0]["code"]["rich_text"][0]["text"]["content"]
    assert content == "print('test')\n"  # One newline preserved, extra stripped


def test_empty_code_block():
    """Test handling of empty code blocks."""
    result = CodeElement.markdown_to_notion("```\n\n```")
    
    assert result is not None
    content = result[0]["code"]["rich_text"][0]["text"]["content"]
    assert content == ""  # Empty content should be handled gracefully


def test_caption_parsing():
    """Test various caption formats."""
    test_cases = [
        ("```python\ncode\n```\nCaption: Simple caption", "Simple caption"),
        ("```js\ncode\n```\ncaption: Lowercase works too", "Lowercase works too"),
        ("```bash\ncode\n```\nCaption: Multi word caption here", "Multi word caption here"),
    ]
    
    for markdown, expected_caption in test_cases:
        result = CodeElement.markdown_to_notion(markdown)
        
        assert result is not None
        code_block = result[0]
        assert "caption" in code_block["code"]
        
        actual_caption = code_block["code"]["caption"][0]["text"]["content"]
        assert actual_caption == expected_caption