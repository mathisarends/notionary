from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import BlockType, CreateBreadcrumbBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.breadcrumb import BreadcrumbParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def breadcrumb_parser(syntax_registry: SyntaxRegistry) -> BreadcrumbParser:
    return BreadcrumbParser(syntax_registry=syntax_registry)


@pytest.mark.parametrize(
    "breadcrumb_line",
    [
        "[breadcrumb]",
        "[BREADCRUMB]",
        "[Breadcrumb]",
        "[BrEaDcRuMb]",
        "[breadcrumb]  ",
        "[breadcrumb]\t",
        "[breadcrumb]   \t  ",
    ],
)
@pytest.mark.asyncio
async def test_valid_breadcrumb_syntax_should_create_breadcrumb_block(
    breadcrumb_parser: BreadcrumbParser,
    context: BlockParsingContext,
    breadcrumb_line: str,
) -> None:
    context.line = breadcrumb_line

    await breadcrumb_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateBreadcrumbBlock)
    assert context.result_blocks[0].type == BlockType.BREADCRUMB


@pytest.mark.parametrize(
    "breadcrumb_line",
    [
        "[breadcrumb]",
        "[BREADCRUMB]",
        "[Breadcrumb]",
    ],
)
def test_case_insensitive_breadcrumb_should_be_handled(
    breadcrumb_parser: BreadcrumbParser,
    context: BlockParsingContext,
    breadcrumb_line: str,
) -> None:
    context.line = breadcrumb_line

    can_handle = breadcrumb_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.parametrize(
    "invalid_line",
    [
        "breadcrumb]",
        "[breadcrumb",
        "[ breadcrumb ]",
        "[breadcrumb] extra text",
        "text [breadcrumb]",
        "[bread crumb]",
        "[breadcrumbs]",
        "# [breadcrumb]",
        "",
        "[caption]",
    ],
)
def test_invalid_breadcrumb_syntax_should_not_be_handled(
    breadcrumb_parser: BreadcrumbParser,
    context: BlockParsingContext,
    invalid_line: str,
) -> None:
    context.line = invalid_line

    can_handle = breadcrumb_parser._can_handle(context)

    assert can_handle is False


def test_breadcrumb_inside_parent_context_should_not_be_handled(
    breadcrumb_parser: BreadcrumbParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[breadcrumb]"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = breadcrumb_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_breadcrumb_block_should_have_correct_structure(
    breadcrumb_parser: BreadcrumbParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[breadcrumb]"

    await breadcrumb_parser._process(context)

    block = context.result_blocks[0]
    assert hasattr(block, "breadcrumb")
    assert block.breadcrumb is not None


def test_is_breadcrumb_with_valid_pattern_should_return_true(
    breadcrumb_parser: BreadcrumbParser,
) -> None:
    is_breadcrumb = breadcrumb_parser._is_breadcrumb("[breadcrumb]")

    assert is_breadcrumb is True


def test_is_breadcrumb_with_invalid_pattern_should_return_false(
    breadcrumb_parser: BreadcrumbParser,
) -> None:
    is_breadcrumb = breadcrumb_parser._is_breadcrumb("not a breadcrumb")

    assert is_breadcrumb is False


def test_create_breadcrumb_block_should_return_valid_block(
    breadcrumb_parser: BreadcrumbParser,
) -> None:
    block = breadcrumb_parser._create_breadcrumb_block()

    assert isinstance(block, CreateBreadcrumbBlock)
    assert block.type == BlockType.BREADCRUMB
    assert block.breadcrumb is not None
