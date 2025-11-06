from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType, CodingLanguage
from notionary.blocks.schemas import Block, CodeBlock, CodeData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.code import CodeRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.schemas import RichText


def _create_code_data(
    rich_text: list[RichText], language: CodingLanguage = CodingLanguage.PLAIN_TEXT
) -> CodeData:
    return CodeData(rich_text=rich_text, language=language)


def _create_code_data_with_caption(
    rich_text: list[RichText],
    caption: list[RichText],
    language: CodingLanguage = CodingLanguage.PLAIN_TEXT,
) -> CodeData:
    return CodeData(rich_text=rich_text, caption=caption, language=language)


def _create_code_block(code_data: CodeData | None) -> CodeBlock:
    mock_obj = Mock(spec=Block)
    code_block = cast(CodeBlock, mock_obj)
    code_block.type = BlockType.CODE
    code_block.code = code_data
    return code_block


@pytest.fixture
def code_renderer(
    syntax_registry: SyntaxDefinitionRegistry,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> CodeRenderer:
    return CodeRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=mock_rich_text_markdown_converter,
    )


@pytest.mark.asyncio
async def test_code_block_should_be_handled(
    code_renderer: CodeRenderer, mock_block: CodeBlock
) -> None:
    mock_block.type = BlockType.CODE

    assert code_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_code_block_should_not_be_handled(
    code_renderer: CodeRenderer, mock_block: CodeBlock
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not code_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_code_with_python_language_should_render_markdown_code_block(
    code_renderer: CodeRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("print('Hello World')")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="print('Hello World')"
    )

    code_data = _create_code_data(rich_text, CodingLanguage.PYTHON)
    block = _create_code_block(code_data)
    render_context.block = block

    await code_renderer._process(render_context)

    assert "```python" in render_context.markdown_result
    assert "print('Hello World')" in render_context.markdown_result
    assert "```" in render_context.markdown_result


@pytest.mark.asyncio
async def test_code_with_caption_should_include_caption_in_markdown(
    code_renderer: CodeRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("const x = 42;")]
    caption_rich_text = [RichText.from_plain_text("Example code")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        side_effect=["const x = 42;", "Example code"]
    )

    code_data = _create_code_data_with_caption(
        rich_text, caption_rich_text, CodingLanguage.JAVASCRIPT
    )
    block = _create_code_block(code_data)
    render_context.block = block

    await code_renderer._process(render_context)

    assert "```javascript" in render_context.markdown_result
    assert "const x = 42;" in render_context.markdown_result
    assert "[caption] Example code" in render_context.markdown_result


@pytest.mark.asyncio
async def test_code_with_empty_content_should_render_empty_string(
    code_renderer: CodeRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="")

    code_data = _create_code_data([])
    block = _create_code_block(code_data)
    render_context.block = block

    await code_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_code_with_missing_data_should_render_empty_string(
    code_renderer: CodeRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_code_block(None)
    render_context.block = block

    await code_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_extract_code_language_with_python_should_return_python(
    code_renderer: CodeRenderer,
) -> None:
    code_data = _create_code_data(
        [RichText.from_plain_text("test")], CodingLanguage.PYTHON
    )
    block = _create_code_block(code_data)

    language = code_renderer._extract_code_language(block)

    assert language == "python"


@pytest.mark.asyncio
async def test_extract_code_language_without_data_should_return_empty_string(
    code_renderer: CodeRenderer,
) -> None:
    block = _create_code_block(None)

    language = code_renderer._extract_code_language(block)

    assert language == ""


@pytest.mark.asyncio
async def test_extract_code_content_with_valid_data_should_return_markdown(
    code_renderer: CodeRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("test code")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="test code")

    code_data = _create_code_data(rich_text)
    block = _create_code_block(code_data)

    content = await code_renderer._extract_code_content(block)

    assert content == "test code"


@pytest.mark.asyncio
async def test_extract_code_content_without_data_should_return_empty_string(
    code_renderer: CodeRenderer,
) -> None:
    block = _create_code_block(None)

    content = await code_renderer._extract_code_content(block)

    assert content == ""
