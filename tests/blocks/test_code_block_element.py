import pytest

from notionary.blocks.code.code_element import CodeElement
from notionary.blocks.code.models import CodeBlock, CodeLanguage, CreateCodeBlock
from notionary.blocks.models import Block
from notionary.blocks.rich_text.models import (
    RichText,
    TextAnnotations,
    TextContent,
)


def create_rich_text_object(content: str) -> RichText:
    """Helper function to create RichText instances."""
    return RichText(
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
        "created_by": {"object": "user", "id": "user-id", "type": "person", "person": {}},
        "last_edited_by": {"object": "user", "id": "user-id", "type": "person", "person": {}},
    }
    defaults.update(kwargs)
    return Block(**defaults)


@pytest.mark.asyncio
async def test_match_markdown_code_start():
    """Test recognition of code block start syntax."""
    assert await CodeElement.markdown_to_notion("```python") is not None
    assert await CodeElement.markdown_to_notion("```js") is not None
    assert await CodeElement.markdown_to_notion("```") is not None
    assert await CodeElement.markdown_to_notion("```bash") is not None


@pytest.mark.asyncio
async def test_match_markdown_not_code_start():
    """Test rejection of non-code-start formats."""
    assert await CodeElement.markdown_to_notion("This is just text.") is None
    assert await CodeElement.markdown_to_notion("`inline code`") is None
    assert not await CodeElement.markdown_to_notion("```python\ncode content")  # Not just start
    assert not await CodeElement.markdown_to_notion("Some text ```python")  # Not at beginning


def test_match_notion():
    """Test recognition of Notion code blocks."""
    code_block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(rich_text=[create_rich_text_object("print('test')")], language="python"),
    )
    assert CodeElement.match_notion(code_block)

    paragraph_block = create_block_with_required_fields(type="paragraph")
    assert not CodeElement.match_notion(paragraph_block)

    callout_block = create_block_with_required_fields(type="callout")
    assert not CodeElement.match_notion(callout_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_with_language():
    """Test conversion of code block start with language."""
    result = await CodeElement.markdown_to_notion("```python")

    assert isinstance(result, CreateCodeBlock)
    assert result.type == "code"
    assert result.code.language == "python"
    assert result.code.rich_text == []  # Empty initially - content added by processor
    assert result.code.caption == []


@pytest.mark.asyncio
async def test_markdown_to_notion_without_language():
    """Test conversion of code block start without language."""
    result = await CodeElement.markdown_to_notion("```")

    assert isinstance(result, CreateCodeBlock)
    assert result.code.language == "plain text"  # Default language
    assert result.code.rich_text == []
    assert result.code.caption == []


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = await CodeElement.markdown_to_notion("This is just text.")
    assert result is None

    result = await CodeElement.markdown_to_notion("```python\ncode content")
    assert result is None  # Not just a start marker


@pytest.mark.asyncio
async def test_notion_to_markdown_simple():
    """Test conversion of Notion code block to Markdown."""
    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language=CodeLanguage.PYTHON,
            rich_text=[create_rich_text_object("print('Hi')")],
        ),
    )

    result = await CodeElement.notion_to_markdown(block)
    assert result == "```python\nprint('Hi')\n```"


@pytest.mark.asyncio
async def test_notion_to_markdown_plain_text():
    """Test conversion of plain text code block."""
    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language=CodeLanguage.PLAIN_TEXT,
            rich_text=[create_rich_text_object("some code")],
        ),
    )

    result = await CodeElement.notion_to_markdown(block)
    assert result == "```\nsome code\n```"  # No language for plain text


@pytest.mark.asyncio
async def test_notion_to_markdown_with_caption():
    """Test conversion of Notion code block with caption."""
    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language=CodeLanguage.PYTHON,
            rich_text=[create_rich_text_object("print('test')")],
            caption=[create_rich_text_object("Example")],
        ),
    )

    result = await CodeElement.notion_to_markdown(block)
    assert result == "```python\nprint('test')\n```\nCaption: Example"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    paragraph_block = create_block_with_required_fields(type="paragraph")
    result = await CodeElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Test block without code property
    code_block_no_code = create_block_with_required_fields(type="code")
    result = await CodeElement.notion_to_markdown(code_block_no_code)
    assert result is None


@pytest.mark.asyncio
async def test_language_normalization():
    """Test language normalization."""
    # Valid languages should pass through
    result = await CodeElement.markdown_to_notion("```python")
    assert result.code.language == "python"

    result = await CodeElement.markdown_to_notion("```javascript")
    assert result.code.language == "javascript"

    # Unknown language should default to "plain text"
    result = await CodeElement.markdown_to_notion("```unknownlang")
    assert result.code.language == "plain text"


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


def test_extract_content_empty_list():
    """Test extract_content with empty list."""
    result = CodeElement.extract_content([])
    assert result == ""


def test_extract_caption_empty_list():
    """Test extract_caption with empty list."""
    result = CodeElement.extract_caption([])
    assert result == ""


# Parametrized tests for different programming languages
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "language,expected_lang",
    [
        ("python", CodeLanguage.PYTHON),
        ("javascript", CodeLanguage.JAVASCRIPT),
        ("bash", CodeLanguage.BASH),
        ("json", CodeLanguage.JSON),
        ("", CodeLanguage.PLAIN_TEXT),  # No language specified
        ("unknownlang", CodeLanguage.PLAIN_TEXT),  # Unknown language
    ],
)
async def test_language_support(language, expected_lang):
    """Test support for different programming languages."""
    markdown = f"```{language}" if language else "```"

    result = await CodeElement.markdown_to_notion(markdown)

    assert result is not None
    assert isinstance(result, CreateCodeBlock)
    assert result.code.language == expected_lang


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("```python", True),
        ("```", True),
        ("```js", True),
        ("`inline code`", False),
        ("Regular text", False),
        ("```python\ncode content", False),  # Not just start
        ("text ```python", False),  # Not at start
    ],
)
async def test_markdown_patterns(markdown, should_match):
    """Test recognition of various Markdown patterns."""
    result = await CodeElement.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None


# Fixtures for common test data
@pytest.fixture
def simple_code_block():
    """Fixture for simple Notion code block."""
    return create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language=CodeLanguage.PYTHON,
            rich_text=[create_rich_text_object("print('test')")],
        ),
    )


@pytest.fixture
def code_block_with_caption():
    """Fixture for Notion code block with caption."""
    return create_block_with_required_fields(
        type="code",
        code=CodeBlock(
            language=CodeLanguage.JAVASCRIPT,
            rich_text=[create_rich_text_object("console.log('hello');")],
            caption=[create_rich_text_object("Example JS code")],
        ),
    )


@pytest.mark.asyncio
async def test_with_fixtures(simple_code_block, code_block_with_caption):
    """Test using fixtures to reduce duplication."""
    # Test simple code block
    result1 = await CodeElement.notion_to_markdown(simple_code_block)
    assert result1 == "```python\nprint('test')\n```"

    # Test code block with caption
    result2 = await CodeElement.notion_to_markdown(code_block_with_caption)
    assert result2 == "```javascript\nconsole.log('hello');\n```\nCaption: Example JS code"


@pytest.mark.asyncio
async def test_roundtrip_basic():
    """Test basic roundtrip conversion compatibility."""
    # Start with code block start
    original_start = "```python"

    # Convert to Notion
    notion_result = await CodeElement.markdown_to_notion(original_start)
    assert notion_result is not None

    # Simulate adding content (this would normally be done by the processor)
    notion_result.code.rich_text = [create_rich_text_object("print('Hello')")]

    # Create a Block for notion_to_markdown
    block = create_block_with_required_fields(type="code", code=notion_result.code)

    # Convert back to Markdown
    result_markdown = await CodeElement.notion_to_markdown(block)
    assert result_markdown == "```python\nprint('Hello')\n```"


@pytest.mark.asyncio
async def test_multiline_content():
    """Test handling of multiline content in notion_to_markdown."""
    rich_text_list = [
        create_rich_text_object("def hello():\n"),
        create_rich_text_object("    print('World')\n"),
        create_rich_text_object("    return True"),
    ]

    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(language=CodeLanguage.PYTHON, rich_text=rich_text_list),
    )

    result = await CodeElement.notion_to_markdown(block)
    expected = "```python\ndef hello():\n    print('World')\n    return True\n```"
    assert result == expected


@pytest.mark.asyncio
async def test_empty_content():
    """Test handling of empty content."""
    block = create_block_with_required_fields(
        type="code",
        code=CodeBlock(language=CodeLanguage.PYTHON, rich_text=[]),
    )

    result = await CodeElement.notion_to_markdown(block)
    assert result == "```python\n\n```"
