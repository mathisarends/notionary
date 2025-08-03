"""
Pytest tests for CodeElement.
Tests conversion between Markdown code blocks and Notion code blocks.
"""

import pytest
from notionary.blocks.code import CodeElement
from notionary.blocks.code.code_models import CodeBlock, CreateCodeBlock
from notionary.blocks.block_models import Block
from notionary.blocks.rich_text.rich_text_models import (
    RichTextObject,
    TextContent,
    TextAnnotations,
)


def create_rich_text_object(content: str) -> RichTextObject:
    """Helper function to create RichTextObject instances."""
    return RichTextObject(
        type="text",
        text=TextContent(content=content),
        annotations=TextAnnotations(),
        plain_text=content,
    )


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
    code_block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            rich_text=[create_rich_text_object("print('test')")], language="python"
        ),
    )
    assert CodeElement.match_notion(code_block)

    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert not CodeElement.match_notion(paragraph_block)

    callout_block = create_block_with_required_fields(type="callout")
    assert not CodeElement.match_notion(callout_block)


def test_markdown_to_notion_with_language():
    """Test conversion of code block with language specification."""
    result = CodeElement.markdown_to_notion("```python\nprint('Hello')\n```")

    assert len(result) == 2  # Code block + empty paragraph
    code_block = result[0]

    assert isinstance(code_block, CreateCodeBlock)
    assert code_block.type == "code"
    assert code_block.code.language == "python"
    assert code_block.code.rich_text[0].plain_text == "print('Hello')"


def test_markdown_to_notion_without_language():
    """Test conversion of code block without language specification."""
    result = CodeElement.markdown_to_notion("```\njust some code\n```")

    code_block = result[0]
    assert code_block.code.language == "plain text"
    assert code_block.code.rich_text[0].plain_text == "just some code"


def test_markdown_to_notion_with_caption():
    """Test conversion of code block with caption."""
    markdown = "```python\nprint('test')\n```\nCaption: Example code"
    result = CodeElement.markdown_to_notion(markdown)

    code_block = result[0]
    assert isinstance(code_block, CreateCodeBlock)
    assert code_block.type == "code"
    assert len(code_block.code.caption) > 0
    assert code_block.code.caption[0].plain_text == "Example code"


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = CodeElement.markdown_to_notion("This is just text.")
    assert result is None


def test_notion_to_markdown():
    """Test conversion of Notion code block to Markdown."""
    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language="python", rich_text=[create_rich_text_object("print('Hi')")]
        ),
    )

    result = CodeElement.notion_to_markdown(block)
    assert result == "```python\nprint('Hi')\n```"


def test_notion_to_markdown_with_caption():
    """Test conversion of Notion code block with caption."""
    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language="python",
            rich_text=[create_rich_text_object("print('test')")],
            caption=[create_rich_text_object("Example")],
        ),
    )

    result = CodeElement.notion_to_markdown(block)
    assert result == "```python\nprint('test')\n```\nCaption: Example"


def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    paragraph_block = create_block_with_required_fields(type="paragraph")
    result = CodeElement.notion_to_markdown(paragraph_block)
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
    assert (
        "console.log('Hi');" in second_match["code"]["rich_text"][0]["text"]["content"]
    )


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
@pytest.mark.parametrize(
    "language,code,expected_lang",
    [
        ("python", "print('hello')", "python"),
        ("javascript", "console.log('test');", "javascript"),
        ("bash", "echo 'hello'", "bash"),
        ("json", '{"key": "value"}', "json"),
        ("", "plain code", "plain text"),  # No language specified
    ],
)
def test_language_support(language, code, expected_lang):
    """Test support for different programming languages."""
    if language:
        markdown = f"```{language}\n{code}\n```"
    else:
        markdown = f"```\n{code}\n```"

    result = CodeElement.markdown_to_notion(markdown)

    assert result is not None
    code_block = result[0]
    assert isinstance(code_block, CreateCodeBlock)
    assert code_block.code.language == expected_lang
    assert code_block.code.rich_text[0].plain_text == code


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("```python\ncode\n```", True),
        ("```\ncode\n```", True),
        ("```js\ncode\n```\nCaption: test", True),
        ("`inline code`", False),
        ("Regular text", False),
        ("```incomplete", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test recognition of various Markdown patterns."""
    result = CodeElement.match_markdown(markdown)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def simple_code_block():
    """Fixture for simple Notion code block."""
    return create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language="python", rich_text=[create_rich_text_object("print('test')")]
        ),
    )


@pytest.fixture
def code_block_with_caption():
    """Fixture for Notion code block with caption."""
    return create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language="javascript",
            rich_text=[create_rich_text_object("console.log('hello');")],
            caption=[create_rich_text_object("Example JS code")],
        ),
    )


def test_with_fixtures(simple_code_block, code_block_with_caption):
    """Test using fixtures to reduce duplication."""
    # Test simple code block
    result1 = CodeElement.notion_to_markdown(simple_code_block)
    assert result1 == "```python\nprint('test')\n```"

    # Test code block with caption
    result2 = CodeElement.notion_to_markdown(code_block_with_caption)
    assert (
        result2 == "```javascript\nconsole.log('hello');\n```\nCaption: Example JS code"
    )


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
        actual_content = notion_result[0].code.rich_text[0].plain_text
        assert actual_content == code_content


def test_trailing_newline_handling():
    """Test proper handling of trailing newlines in code content."""
    # Code with trailing newline
    markdown_with_newline = "```python\nprint('test')\n\n```"
    result = CodeElement.markdown_to_notion(markdown_with_newline)

    # Should strip trailing newline
    content = result[0].code.rich_text[0].plain_text
    assert content == "print('test')\n"  # One newline preserved, extra stripped


def test_empty_code_block():
    """Test handling of empty code blocks."""
    result = CodeElement.markdown_to_notion("```\n\n```")

    assert result is not None
    content = result[0].code.rich_text[0].plain_text
    assert content == ""  # Empty content should be handled gracefully


def test_caption_parsing():
    """Test various caption formats."""
    test_cases = [
        ("```python\ncode\n```\nCaption: Simple caption", "Simple caption"),
        ("```js\ncode\n```\ncaption: Lowercase works too", "Lowercase works too"),
        (
            "```bash\ncode\n```\nCaption: Multi word caption here",
            "Multi word caption here",
        ),
    ]

    for markdown, expected_caption in test_cases:
        result = CodeElement.markdown_to_notion(markdown)

        assert result is not None
        code_block = result[0]
        assert isinstance(code_block, CreateCodeBlock)
        assert len(code_block.code.caption) > 0

        actual_caption = code_block.code.caption[0].plain_text
        assert actual_caption == expected_caption


def test_roundtrip_conversion():
    """Test that Markdown -> Notion -> Markdown preserves content."""
    test_cases = [
        "```python\nprint('Hello')\n```",
        "```js\nconsole.log('test');\n```",
        "```\nplain code\n```",
        "```python\nprint('test')\n```\nCaption: Example",
    ]

    for original_markdown in test_cases:
        # Convert to Notion
        notion_result = CodeElement.markdown_to_notion(original_markdown)
        assert notion_result is not None

        # Create a Block for notion_to_markdown
        code_create_block = notion_result[0]  # First item is the code block
        block = create_block_with_required_fields(
            type="code", code=code_create_block.code
        )

        # Convert back to Markdown
        result_markdown = CodeElement.notion_to_markdown(block)
        assert result_markdown is not None

        # For comparison, we need to normalize both strings
        # (Caption format might be slightly different)
        if "Caption:" in original_markdown:
            assert "Caption:" in result_markdown
            # Check that code content is preserved
            original_code = (
                original_markdown.split("```")[1].split("\n", 1)[1].rsplit("\n", 1)[0]
            )
            result_code = (
                result_markdown.split("```")[1].split("\n", 1)[1].rsplit("\n", 1)[0]
            )
            assert original_code == result_code
        else:
            assert result_markdown == original_markdown


def test_language_normalization():
    """Test that languages are properly normalized."""
    test_cases = [
        ("Python", "python"),  # Uppercase -> lowercase
        ("JavaScript", "javascript"),  # Mixed case -> lowercase
        ("BASH", "bash"),  # All caps -> lowercase
        ("unknown_lang", "plain text"),  # Unknown -> plain text
    ]

    for input_lang, expected_lang in test_cases:
        markdown = f"```{input_lang}\ncode\n```"
        result = CodeElement.markdown_to_notion(markdown)

        if result:
            assert result[0].code.language == expected_lang
        else:
            # If conversion failed, it should be because of invalid language
            assert expected_lang == "plain text"


def test_extract_content_helper():
    """Test the static helper method for extracting content."""
    rich_text_list = [
        create_rich_text_object("line 1\n"),
        create_rich_text_object("line 2"),
    ]

    result = CodeElement.extract_content(rich_text_list)
    assert result == "line 1\nline 2"


def test_extract_caption_helper():
    """Test the static helper method for extracting caption."""
    caption_list = [
        create_rich_text_object("Caption part 1 "),
        create_rich_text_object("and part 2"),
    ]

    result = CodeElement.extract_caption(caption_list)
    assert result == "Caption part 1 and part 2"


def test_plain_text_language_handling():
    """Test that 'plain text' language is handled correctly in conversion."""
    # Test markdown -> notion with no language
    markdown = "```\nsome code\n```"
    notion_result = CodeElement.markdown_to_notion(markdown)
    assert notion_result[0].code.language == "plain text"

    # Test notion -> markdown with 'plain text' language
    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language="plain text", rich_text=[create_rich_text_object("some code")]
        ),
    )

    markdown_result = CodeElement.notion_to_markdown(block)
    assert markdown_result == "```\nsome code\n```"  # No language shown for plain text
