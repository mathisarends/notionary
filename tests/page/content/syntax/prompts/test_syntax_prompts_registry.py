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

    # Create markdown preprocessor with all handlers
    markdown_pre_processor = MarkdownPreProcessor()
    markdown_pre_processor.register(ColumnSyntaxPreProcessor())
    markdown_pre_processor.register(WhitespacePreProcessor())
    markdown_pre_processor.register(IndentationNormalizer())
    markdown_pre_processor.register(VideoFormatPreProcessor())

    # Create block post-processor with all handlers
    block_post_processor = BlockPostProcessor()
    block_post_processor.register(RichTextLengthTruncationPostProcessor())

    # Create and return the converter
    return MarkdownToNotionConverter(
        line_parser=line_parser,
        pre_processor=markdown_pre_processor,
        post_processor=block_post_processor,
    )


class TestSyntaxPromptRegistryIntegration:
    """
    Integration tests that validate the SyntaxPromptRegistry few-shot examples.

    PURPOSE:
    These tests ensure that the few-shot examples provided by the SyntaxPromptRegistry
    actually produce the correct Notion block structures when processed by the
    MarkdownToNotionConverter. This validates that:

    1. The examples use correct syntax
    2. The converter recognizes the syntax correctly
    3. The resulting blocks match the intended block type

    Each test iterates through all few-shot examples for a specific syntax type and
    verifies that they produce blocks of the expected type.

    ARCHITECTURE:
    The converter is initialized with the same dependencies as in production:
    - LineParser: Chain of responsibility for parsing different markdown syntax
    - MarkdownPreProcessor: Pre-processes markdown (column syntax, whitespace, etc.)
    - BlockPostProcessor: Post-processes blocks (rich text truncation, etc.)
    """

    def _assert_block_type(
        self,
        blocks: list,
        expected_type: BlockType,
        example: str,
        syntax_name: str,
    ) -> None:
        """
        Helper method to assert block type with detailed error messages.

        Args:
            blocks: List of blocks produced by the converter
            expected_type: Expected BlockType
            example: The markdown example that was converted
            syntax_name: Name of the syntax being tested (for error messages)
        """
        assert len(blocks) >= 1, (
            f"\n{'=' * 80}\n"
            f"SYNTAX: {syntax_name}\n"
            f"EXAMPLE: {example!r}\n"
            f"ERROR: Example produced no blocks!\n"
            f"{'=' * 80}"
        )

        actual_type = blocks[0].type
        assert actual_type == expected_type, (
            f"\n{'=' * 80}\n"
            f"SYNTAX: {syntax_name}\n"
            f"EXAMPLE: {example!r}\n"
            f"EXPECTED: {expected_type}\n"
            f"ACTUAL: {actual_type}\n"
            f"ALL BLOCKS: {[block.type for block in blocks]}\n"
            f"{'=' * 80}"
        )

    @pytest.mark.asyncio
    async def test_audio_examples_produce_audio_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that audio syntax examples produce Audio blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.AUDIO
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.AUDIO, example, "Audio")

    @pytest.mark.asyncio
    async def test_video_examples_produce_video_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that video syntax examples produce Video blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.VIDEO
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.VIDEO, example, "Video")

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
            self._assert_block_type(blocks, BlockType.IMAGE, example, "Image")

    @pytest.mark.asyncio
    async def test_file_examples_produce_file_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that file syntax examples produce File blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.FILE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.FILE, example, "File")

    @pytest.mark.asyncio
    async def test_pdf_examples_produce_pdf_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that PDF syntax examples produce PDF blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.PDF
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.PDF, example, "PDF")

    @pytest.mark.asyncio
    async def test_bookmark_examples_produce_bookmark_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that bookmark syntax examples produce Bookmark blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.BOOKMARK
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.BOOKMARK, example, "Bookmark")

    @pytest.mark.asyncio
    async def test_embed_examples_produce_embed_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that embed syntax examples produce Embed blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.EMBED
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.EMBED, example, "Embed")

    @pytest.mark.asyncio
    async def test_bulleted_list_examples_produce_bulleted_list_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that bulleted list syntax examples produce Bulleted List Item blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.BULLETED_LIST
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(
                blocks, BlockType.BULLETED_LIST_ITEM, example, "Bulleted List"
            )

    @pytest.mark.asyncio
    async def test_numbered_list_examples_produce_numbered_list_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that numbered list syntax examples produce Numbered List Item blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.NUMBERED_LIST
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(
                blocks, BlockType.NUMBERED_LIST_ITEM, example, "Numbered List"
            )

    @pytest.mark.asyncio
    async def test_todo_examples_produce_todo_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that todo syntax examples produce unchecked Todo blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TO_DO
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            # Assert basic block structure
            self._assert_block_type(blocks, BlockType.TO_DO, example, "Todo")

            # Additionally validate that the todo is unchecked
            assert blocks[0].to_do.checked is False, (
                f"\n{'=' * 80}\n"
                f"SYNTAX: Todo\n"
                f"EXAMPLE: {example!r}\n"
                f"ERROR: Todo should be unchecked but was checked!\n"
                f"{'=' * 80}"
            )

    @pytest.mark.asyncio
    async def test_todo_done_examples_produce_todo_done_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that todo-done syntax examples produce checked Todo blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TO_DO_DONE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            # Assert basic block structure
            self._assert_block_type(blocks, BlockType.TO_DO, example, "Todo Done")

            # Additionally validate that the todo is checked
            assert blocks[0].to_do.checked is True, (
                f"\n{'=' * 80}\n"
                f"SYNTAX: Todo Done\n"
                f"EXAMPLE: {example!r}\n"
                f"ERROR: Todo should be checked but was unchecked!\n"
                f"{'=' * 80}"
            )

    @pytest.mark.asyncio
    async def test_toggle_examples_produce_toggle_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that toggle syntax examples produce Toggle blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TOGGLE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.TOGGLE, example, "Toggle")

    @pytest.mark.asyncio
    async def test_callout_examples_produce_callout_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that callout syntax examples produce Callout blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.CALLOUT
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.CALLOUT, example, "Callout")

    @pytest.mark.asyncio
    async def test_code_examples_produce_code_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that code syntax examples produce Code blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.CODE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.CODE, example, "Code")

    @pytest.mark.asyncio
    async def test_column_examples_produce_column_list_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that column syntax examples produce Column List blocks with at least 2 columns."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.COLUMN_LIST
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            # Assert basic block structure
            self._assert_block_type(
                blocks, BlockType.COLUMN_LIST, example, "Column List"
            )

            # Validate that column list has at least 2 columns
            num_columns = len(blocks[0].column_list.children)
            assert num_columns >= 2, (
                f"\n{'=' * 80}\n"
                f"SYNTAX: Column List\n"
                f"EXAMPLE: {example!r}\n"
                f"ERROR: Column List must have at least 2 columns, but has {num_columns}\n"
                f"{'=' * 80}"
            )

    @pytest.mark.asyncio
    async def test_equation_examples_produce_equation_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that equation syntax examples produce Equation blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.EQUATION
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.EQUATION, example, "Equation")

    @pytest.mark.asyncio
    async def test_quote_examples_produce_quote_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that quote syntax examples produce Quote blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.QUOTE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.QUOTE, example, "Quote")

    @pytest.mark.asyncio
    async def test_heading_examples_produce_heading_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that heading syntax examples produce Heading blocks (H1, H2, or H3)."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.HEADING
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            assert len(blocks) >= 1, (
                f"\n{'=' * 80}\n"
                f"SYNTAX: Heading\n"
                f"EXAMPLE: {example!r}\n"
                f"ERROR: Example produced no blocks!\n"
                f"{'=' * 80}"
            )

            actual_type = blocks[0].type
            valid_heading_types = [
                BlockType.HEADING_1,
                BlockType.HEADING_2,
                BlockType.HEADING_3,
            ]
            assert actual_type in valid_heading_types, (
                f"\n{'=' * 80}\n"
                f"SYNTAX: Heading\n"
                f"EXAMPLE: {example!r}\n"
                f"EXPECTED: One of {valid_heading_types}\n"
                f"ACTUAL: {actual_type}\n"
                f"ALL BLOCKS: {[block.type for block in blocks]}\n"
                f"{'=' * 80}"
            )

    @pytest.mark.asyncio
    async def test_divider_examples_produce_divider_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that divider syntax examples produce Divider blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.DIVIDER
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.DIVIDER, example, "Divider")

    @pytest.mark.asyncio
    async def test_breadcrumb_examples_produce_breadcrumb_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that breadcrumb syntax examples produce Breadcrumb blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.BREADCRUMB
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(blocks, BlockType.BREADCRUMB, example, "Breadcrumb")

    @pytest.mark.asyncio
    async def test_table_of_contents_examples_produce_toc_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that table of contents syntax examples produce Table of Contents blocks."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)
            self._assert_block_type(
                blocks, BlockType.TABLE_OF_CONTENTS, example, "Table of Contents"
            )

    @pytest.mark.asyncio
    async def test_table_examples_produce_table_blocks(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """Validate that table syntax examples produce Table blocks with at least 2 rows."""
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.TABLE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            # Assert basic block structure
            self._assert_block_type(blocks, BlockType.TABLE, example, "Table")

            # Validate that table has at least 2 rows (header + data)
            num_rows = len(blocks[0].table.children)
            assert num_rows >= 2, (
                f"\n{'=' * 80}\n"
                f"SYNTAX: Table\n"
                f"EXAMPLE: {example!r}\n"
                f"ERROR: Table must have at least 2 rows (header + data), but has {num_rows}\n"
                f"{'=' * 80}"
            )

    @pytest.mark.asyncio
    async def test_space_examples_produce_valid_output(
        self,
        syntax_prompt_registry: SyntaxPromptRegistry,
        markdown_converter: MarkdownToNotionConverter,
    ) -> None:
        """
        Validate that space syntax examples produce valid output.

        Note: Space might produce empty paragraph or no block at all depending on
        implementation. This test validates that it doesn't crash and produces valid output.
        """
        prompt_data = syntax_prompt_registry.get_prompt_data(
            SyntaxDefinitionRegistryKey.SPACE
        )

        for example in prompt_data.few_shot_examples:
            blocks = await markdown_converter.convert(example)

            # Just validate it returns a list (empty is acceptable for space)
            assert isinstance(blocks, list), (
                f"\n{'=' * 80}\n"
                f"SYNTAX: Space\n"
                f"EXAMPLE: {example!r}\n"
                f"ERROR: Converter did not return a list!\n"
                f"{'=' * 80}"
            )
