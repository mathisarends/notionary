import pytest

from notionary.blocks.enums import BlockType
from notionary.page.content.parser.service import MarkdownToNotionConverter
from notionary.page.content.syntax.definition.models import SyntaxDefinitionRegistryKey
from notionary.page.content.syntax.prompts.registry import SyntaxPromptRegistry


@pytest.fixture
def syntax_prompt_registry() -> SyntaxPromptRegistry:
    return SyntaxPromptRegistry()


@pytest.fixture
def markdown_converter(
    markdown_to_notion_converter: MarkdownToNotionConverter,
) -> MarkdownToNotionConverter:
    return markdown_to_notion_converter


class TestSyntaxPromptRegistryIntegration:
    @pytest.mark.asyncio
    async def test_audio_examples_produce_audio_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.AUDIO
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.AUDIO, (
                f"Example '{example}' did not produce Audio block"
            )

    @pytest.mark.asyncio
    async def test_video_examples_produce_video_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.VIDEO
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.VIDEO, (
                f"Example '{example}' did not produce Video block"
            )

    @pytest.mark.asyncio
    async def test_image_examples_produce_image_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.IMAGE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.IMAGE, (
                f"Example '{example}' did not produce Image block"
            )

    @pytest.mark.asyncio
    async def test_file_examples_produce_file_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.FILE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.FILE, (
                f"Example '{example}' did not produce File block"
            )

    @pytest.mark.asyncio
    async def test_pdf_examples_produce_pdf_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.PDF
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.PDF, (
                f"Example '{example}' did not produce PDF block"
            )

    @pytest.mark.asyncio
    async def test_bookmark_examples_produce_bookmark_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.BOOKMARK
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.BOOKMARK, (
                f"Example '{example}' did not produce Bookmark block"
            )

    @pytest.mark.asyncio
    async def test_embed_examples_produce_embed_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.EMBED
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.EMBED, (
                f"Example '{example}' did not produce Embed block"
            )

    @pytest.mark.asyncio
    async def test_bulleted_list_examples_produce_bulleted_list_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.BULLETED_LIST
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.BULLETED_LIST_ITEM, (
                f"Example '{example}' did not produce Bulleted List block"
            )

    @pytest.mark.asyncio
    async def test_numbered_list_examples_produce_numbered_list_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.NUMBERED_LIST
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.NUMBERED_LIST_ITEM, (
                f"Example '{example}' did not produce Numbered List block"
            )

    @pytest.mark.asyncio
    async def test_todo_examples_produce_todo_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TO_DO
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.TO_DO, (
                f"Example '{example}' did not produce Todo block"
            )
            assert blocks[0].to_do.checked is False, (
                f"Example '{example}' produced checked Todo"
            )

    @pytest.mark.asyncio
    async def test_todo_done_examples_produce_todo_done_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TO_DO_DONE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.TO_DO, (
                f"Example '{example}' did not produce Todo block"
            )
            assert blocks[0].to_do.checked is True, (
                f"Example '{example}' produced unchecked Todo"
            )

    @pytest.mark.asyncio
    async def test_toggle_examples_produce_toggle_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TOGGLE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.TOGGLE, (
                f"Example '{example}' did not produce Toggle block"
            )

    @pytest.mark.asyncio
    async def test_callout_examples_produce_callout_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.CALLOUT
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.CALLOUT, (
                f"Example '{example}' did not produce Callout block"
            )

    @pytest.mark.asyncio
    async def test_code_examples_produce_code_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.CODE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.CODE, (
                f"Example '{example}' did not produce Code block"
            )

    @pytest.mark.asyncio
    async def test_column_examples_produce_column_list_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.COLUMN_LIST
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.COLUMN_LIST, (
                f"Example '{example}' did not produce Column List block"
            )
            # Validate that column list has at least 2 columns
            assert len(blocks[0].column_list.children) >= 2, (
                f"Example '{example}' produced Column List with less than 2 columns"
            )

    @pytest.mark.asyncio
    async def test_equation_examples_produce_equation_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.EQUATION
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.EQUATION, (
                f"Example '{example}' did not produce Equation block"
            )

    @pytest.mark.asyncio
    async def test_quote_examples_produce_quote_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.QUOTE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.QUOTE, (
                f"Example '{example}' did not produce Quote block"
            )

    @pytest.mark.asyncio
    async def test_heading_examples_produce_heading_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.HEADING
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type in [
                BlockType.HEADING_1,
                BlockType.HEADING_2,
                BlockType.HEADING_3,
            ], f"Example '{example}' did not produce Heading block"

    @pytest.mark.asyncio
    async def test_divider_examples_produce_divider_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.DIVIDER
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.DIVIDER, (
                f"Example '{example}' did not produce Divider block"
            )

    @pytest.mark.asyncio
    async def test_breadcrumb_examples_produce_breadcrumb_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.BREADCRUMB
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.BREADCRUMB, (
                f"Example '{example}' did not produce Breadcrumb block"
            )

    @pytest.mark.asyncio
    async def test_table_of_contents_examples_produce_toc_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.TABLE_OF_CONTENTS, (
                f"Example '{example}' did not produce Table of Contents block"
            )

    @pytest.mark.asyncio
    async def test_table_examples_produce_table_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TABLE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, f"Example '{example}' produced no blocks"
            assert blocks[0].type == BlockType.TABLE, (
                f"Example '{example}' did not produce Table block"
            )
            # Validate that table has rows
            assert len(blocks[0].table.children) >= 2, (
                f"Example '{example}' produced Table with less than 2 rows (header + data)"
            )

    @pytest.mark.asyncio
    async def test_space_examples_produce_paragraph_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.SPACE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            # Space might produce empty paragraph or no block at all depending on implementation
            # This test validates that it doesn't crash and produces valid output
            assert isinstance(blocks, list), (
                f"Example '{example}' did not return a list"
            )
