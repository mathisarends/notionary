from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateSyncedBlockBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.synced_block import SyncedBlockParser
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def synced_block_parser(syntax_registry: SyntaxDefinitionRegistry) -> SyncedBlockParser:
    return SyncedBlockParser(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_duplicate_synced_block_should_be_handled(
    synced_block_parser: SyncedBlockParser,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    context.line = f"{syntax.start_delimiter} Synced from: abc-123-def"

    assert synced_block_parser._can_handle(context)


@pytest.mark.asyncio
async def test_original_synced_block_should_be_handled(
    synced_block_parser: SyncedBlockParser,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    context.line = f"{syntax.start_delimiter} Synced Block"

    assert synced_block_parser._can_handle(context)


@pytest.mark.asyncio
async def test_non_synced_block_should_not_be_handled(
    synced_block_parser: SyncedBlockParser, context: BlockParsingContext
) -> None:
    context.line = "Regular paragraph"

    assert not synced_block_parser._can_handle(context)


@pytest.mark.asyncio
async def test_duplicate_synced_block_should_create_block_with_reference(
    synced_block_parser: SyncedBlockParser,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    context.line = f"{syntax.start_delimiter} Synced from: abc-123-def-456-789"

    await synced_block_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateSyncedBlockBlock)
    assert block.synced_block.synced_from.block_id == "abc-123-def-456-789"


@pytest.mark.asyncio
async def test_duplicate_synced_block_with_extra_whitespace_should_extract_id(
    synced_block_parser: SyncedBlockParser,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    context.line = f"{syntax.start_delimiter} Synced from:   abc-456-def-789-012   "

    await synced_block_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.synced_block.synced_from.block_id == "abc-456-def-789-012"


@pytest.mark.asyncio
async def test_duplicate_synced_block_without_id_should_not_create_block(
    synced_block_parser: SyncedBlockParser,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    context.line = f"{syntax.start_delimiter} Synced from:"

    await synced_block_parser._process(context)

    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_original_synced_block_should_log_warning(
    synced_block_parser: SyncedBlockParser,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    context.line = f"{syntax.start_delimiter} Synced Block"

    await synced_block_parser._process(context)

    assert len(context.result_blocks) == 0
    assert "Original Synced Blocks" in caplog.text
    assert "must be created via the Notion UI" in caplog.text


@pytest.mark.asyncio
async def test_synced_block_inside_parent_context_should_not_be_handled(
    synced_block_parser: SyncedBlockParser,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    context.line = f"{syntax.start_delimiter} Synced from: abc-123-def-456-789"
    context.is_inside_parent_context = Mock(return_value=True)

    assert not synced_block_parser._can_handle(context)


@pytest.mark.asyncio
async def test_extract_block_id_with_valid_id_should_return_id(
    synced_block_parser: SyncedBlockParser,
) -> None:
    line = ">>> Synced from: abc-123-def-456-789"

    block_id = synced_block_parser._extract_block_id(line)

    assert block_id == "abc-123-def-456-789"


@pytest.mark.asyncio
async def test_extract_block_id_without_id_should_return_none(
    synced_block_parser: SyncedBlockParser,
) -> None:
    line = ">>> Synced from:"

    block_id = synced_block_parser._extract_block_id(line)

    assert block_id is None


@pytest.mark.asyncio
async def test_is_duplicate_block_with_synced_from_should_return_true(
    synced_block_parser: SyncedBlockParser,
) -> None:
    line = ">>> Synced from: abc-123-def-456-789"

    assert synced_block_parser._is_duplicate_block(line)


@pytest.mark.asyncio
async def test_is_duplicate_block_without_synced_from_should_return_false(
    synced_block_parser: SyncedBlockParser,
) -> None:
    line = ">>> Synced Block"

    assert not synced_block_parser._is_duplicate_block(line)
