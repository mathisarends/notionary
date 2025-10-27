import pytest

from notionary.blocks.enums import BlockType
from notionary.page.content.parser.factory import ConverterChainFactory
from notionary.page.content.parser.post_processing.handlers import (
    RichTextLengthTruncationPostProcessor,
)
from notionary.page.content.parser.post_processing.service import BlockPostProcessor
from notionary.page.content.parser.pre_processsing.handlers import (
    ColumnSyntaxPreProcessor,
    IndentationNormalizer,
    VideoFormatPreProcessor,
    WhitespacePreProcessor,
)
from notionary.page.content.parser.pre_processsing.service import MarkdownPreProcessor
from notionary.page.content.parser.service import MarkdownToNotionConverter
from notionary.page.content.syntax.definition.models import SyntaxDefinitionRegistryKey
from notionary.page.content.syntax.prompts.registry import SyntaxPromptRegistry


@pytest.fixture
def syntax_prompt_registry() -> SyntaxPromptRegistry:
    return SyntaxPromptRegistry()


@pytest.fixture
def markdown_converter() -> MarkdownToNotionConverter:
    converter_chain_factory = ConverterChainFactory()
    line_parser = converter_chain_factory.create()

    markdown_pre_processor = MarkdownPreProcessor()
    markdown_pre_processor.register(ColumnSyntaxPreProcessor())
    markdown_pre_processor.register(WhitespacePreProcessor())
    markdown_pre_processor.register(IndentationNormalizer())
    markdown_pre_processor.register(VideoFormatPreProcessor())

    block_post_processor = BlockPostProcessor()
    block_post_processor.register(RichTextLengthTruncationPostProcessor())

    return MarkdownToNotionConverter(
        line_parser=line_parser,
        pre_processor=markdown_pre_processor,
        post_processor=block_post_processor,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_audio_examples_produce_audio_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.AUDIO
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.AUDIO


@pytest.mark.integration
@pytest.mark.asyncio
async def test_video_examples_produce_video_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.VIDEO
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.VIDEO


@pytest.mark.integration
@pytest.mark.asyncio
async def test_image_examples_produce_image_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.IMAGE
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.IMAGE


@pytest.mark.integration
@pytest.mark.asyncio
async def test_file_examples_produce_file_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.FILE
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.FILE


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pdf_examples_produce_pdf_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.PDF
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.PDF


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bookmark_examples_produce_bookmark_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.BOOKMARK
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.BOOKMARK


@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_examples_produce_embed_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.EMBED
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.EMBED


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bulleted_list_examples_produce_bulleted_list_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.BULLETED_LIST
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.BULLETED_LIST_ITEM


@pytest.mark.integration
@pytest.mark.asyncio
async def test_numbered_list_examples_produce_numbered_list_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.NUMBERED_LIST
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.NUMBERED_LIST_ITEM


@pytest.mark.integration
@pytest.mark.asyncio
async def test_to_do_examples_produce_to_do_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.TO_DO
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.TO_DO


@pytest.mark.integration
@pytest.mark.asyncio
async def test_toggle_examples_produce_toggle_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.TOGGLE
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.TOGGLE


@pytest.mark.integration
@pytest.mark.asyncio
async def test_callout_examples_produce_callout_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.CALLOUT
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.CALLOUT


@pytest.mark.integration
@pytest.mark.asyncio
async def test_code_examples_produce_code_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.CODE
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.CODE


@pytest.mark.integration
@pytest.mark.asyncio
async def test_column_examples_produce_column_list_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.COLUMN_LIST
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.COLUMN_LIST
        assert len(blocks[0].column_list.children) >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_equation_examples_produce_equation_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.EQUATION
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.EQUATION


@pytest.mark.integration
@pytest.mark.asyncio
async def test_quote_examples_produce_quote_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.QUOTE
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.QUOTE


@pytest.mark.integration
@pytest.mark.asyncio
async def test_heading_examples_produce_heading_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.HEADING
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type in [
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        ]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_divider_examples_produce_divider_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.DIVIDER
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.DIVIDER


@pytest.mark.integration
@pytest.mark.asyncio
async def test_breadcrumb_examples_produce_breadcrumb_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.BREADCRUMB
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.BREADCRUMB


@pytest.mark.integration
@pytest.mark.asyncio
async def test_table_of_contents_examples_produce_toc_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.TABLE_OF_CONTENTS


@pytest.mark.integration
@pytest.mark.asyncio
async def test_table_examples_produce_table_blocks(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.TABLE
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert len(blocks) >= 1
        assert blocks[0].type == BlockType.TABLE
        assert len(blocks[0].table.children) >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_space_examples_produce_valid_output(
    syntax_prompt_registry: SyntaxPromptRegistry,
    markdown_converter: MarkdownToNotionConverter,
) -> None:
    prompt_data = syntax_prompt_registry.get_prompt_data(
        SyntaxDefinitionRegistryKey.SPACE
    )

    for example in prompt_data.few_shot_examples:
        blocks = await markdown_converter.convert(example)
        assert isinstance(blocks, list)
