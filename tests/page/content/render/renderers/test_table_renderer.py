from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, TableBlock, TableData, TableRowBlock, TableRowData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.table import TableRenderer


def _create_table_data(
    has_column_header: bool = False,
    has_row_header: bool = False,
    table_width: int = 0,
) -> TableData:
    return TableData(
        has_column_header=has_column_header,
        has_row_header=has_row_header,
        table_width=table_width,
    )


def _create_table_row_block(cells: list[list[RichText]]) -> TableRowBlock:
    mock_obj = Mock(spec=Block)
    table_row_block = cast(TableRowBlock, mock_obj)
    table_row_block.type = BlockType.TABLE_ROW
    table_row_block.table_row = Mock(spec=TableRowData)
    table_row_block.table_row.cells = cells
    return table_row_block


def _create_table_block(
    table_data: TableData | None,
    children: list[Block] | None = None,
) -> TableBlock:
    mock_obj = Mock(spec=Block)
    table_block = cast(TableBlock, mock_obj)
    table_block.type = BlockType.TABLE
    table_block.table = table_data
    table_block.has_children = children is not None and len(children) > 0
    table_block.children = children if children else []
    return table_block


@pytest.fixture
def table_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> TableRenderer:
    return TableRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_table_block_should_be_handled(table_renderer: TableRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.TABLE

    assert table_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_table_block_should_not_be_handled(table_renderer: TableRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not table_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_table_with_simple_data_should_render_markdown_table(
    table_renderer: TableRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    # Mock the converter to return cell content
    async def mock_to_markdown(rich_text):
        if rich_text and len(rich_text) > 0:
            return rich_text[0].plain_text
        return ""

    mock_rich_text_markdown_converter.to_markdown = AsyncMock(side_effect=mock_to_markdown)

    # Create table with 2x2 cells
    row1_cells = [
        [RichText.from_plain_text("Header 1")],
        [RichText.from_plain_text("Header 2")],
    ]
    row2_cells = [
        [RichText.from_plain_text("Cell 1")],
        [RichText.from_plain_text("Cell 2")],
    ]

    row1 = _create_table_row_block(row1_cells)
    row2 = _create_table_row_block(row2_cells)

    table_data = _create_table_data(has_column_header=True)
    block = _create_table_block(table_data, children=[row1, row2])
    render_context.block = block

    await table_renderer._process(render_context)

    # Verify it contains table structure
    assert "|" in render_context.markdown_result
    assert "Header 1" in render_context.markdown_result
    assert "Header 2" in render_context.markdown_result
    assert "Cell 1" in render_context.markdown_result
    assert "Cell 2" in render_context.markdown_result
    assert "---" in render_context.markdown_result


@pytest.mark.asyncio
async def test_table_without_children_should_render_empty_string(
    table_renderer: TableRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    table_data = _create_table_data()
    block = _create_table_block(table_data, children=None)
    render_context.block = block

    await table_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_table_without_data_should_render_empty_string(
    table_renderer: TableRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_table_block(None, children=None)
    render_context.block = block

    await table_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_table_with_indentation_should_indent_output(
    table_renderer: TableRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    async def mock_to_markdown(rich_text):
        if rich_text and len(rich_text) > 0:
            return rich_text[0].plain_text
        return ""

    mock_rich_text_markdown_converter.to_markdown = AsyncMock(side_effect=mock_to_markdown)

    row_cells = [[RichText.from_plain_text("Cell")]]
    row = _create_table_row_block(row_cells)

    table_data = _create_table_data()
    block = _create_table_block(table_data, children=[row])
    render_context.block = block
    render_context.indent_level = 1

    await table_renderer._process(render_context)

    # Mock indent_text should be called
    render_context.indent_text.assert_called_once()


@pytest.mark.asyncio
async def test_table_with_children_blocks_should_render_children_with_indent(
    table_renderer: TableRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    async def mock_to_markdown(rich_text):
        if rich_text and len(rich_text) > 0:
            return rich_text[0].plain_text
        return ""

    mock_rich_text_markdown_converter.to_markdown = AsyncMock(side_effect=mock_to_markdown)
    render_context.render_children_with_additional_indent = AsyncMock(return_value="    Child content")

    row_cells = [[RichText.from_plain_text("Cell")]]
    row = _create_table_row_block(row_cells)

    table_data = _create_table_data()
    block = _create_table_block(table_data, children=[row])
    render_context.block = block

    await table_renderer._process(render_context)

    assert "Child content" in render_context.markdown_result
    render_context.render_children_with_additional_indent.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_normalize_row_lengths_should_pad_shorter_rows(
    table_renderer: TableRenderer,
) -> None:
    rows = [
        ["A", "B", "C"],
        ["D", "E"],
        ["F"],
    ]

    normalized = table_renderer._normalize_row_lengths(rows, 3)

    assert normalized == [
        ["A", "B", "C"],
        ["D", "E", ""],
        ["F", "", ""],
    ]


@pytest.mark.asyncio
async def test_calculate_column_widths_should_return_max_widths(
    table_renderer: TableRenderer,
) -> None:
    rows = [
        ["Short", "Medium text", "A"],
        ["X", "Y", "Very long text"],
    ]

    widths = table_renderer._calculate_column_widths(rows, 3)

    assert widths[0] == 5  # "Short" length
    assert widths[1] == 11  # "Medium text" length
    assert widths[2] == 14  # "Very long text" length


@pytest.mark.asyncio
async def test_calculate_column_widths_should_respect_minimum_width(
    table_renderer: TableRenderer,
) -> None:
    rows = [["A", "B"]]

    widths = table_renderer._calculate_column_widths(rows, 2)

    # Both should be at least MINIMUM_COLUMN_WIDTH (3)
    assert all(w >= 3 for w in widths)


@pytest.mark.asyncio
async def test_format_row_should_center_cells(
    table_renderer: TableRenderer,
) -> None:
    cells = ["A", "B"]
    widths = [5, 5]

    formatted = table_renderer._format_row(cells, widths)

    # Python's str.center() adds extra space on right for odd padding
    assert formatted == "|   A   |   B   |"


@pytest.mark.asyncio
async def test_create_separator_line_should_create_dashes(
    table_renderer: TableRenderer,
) -> None:
    widths = [3, 5, 4]

    separator = table_renderer._create_separator_line(widths)

    assert separator == "| --- | ----- | ---- |"


@pytest.mark.asyncio
async def test_has_column_header_with_header_should_return_true(
    table_renderer: TableRenderer,
) -> None:
    table_data = _create_table_data(has_column_header=True)
    block = _create_table_block(table_data)

    assert table_renderer._has_column_header(block) is True


@pytest.mark.asyncio
async def test_has_column_header_without_header_should_return_false(
    table_renderer: TableRenderer,
) -> None:
    table_data = _create_table_data(has_column_header=False)
    block = _create_table_block(table_data)

    assert table_renderer._has_column_header(block) is False


@pytest.mark.asyncio
async def test_has_row_header_with_header_should_return_true(
    table_renderer: TableRenderer,
) -> None:
    table_data = _create_table_data(has_row_header=True)
    block = _create_table_block(table_data)

    assert table_renderer._has_row_header(block) is True


@pytest.mark.asyncio
async def test_get_table_width_should_return_width(
    table_renderer: TableRenderer,
) -> None:
    table_data = _create_table_data(table_width=3)
    block = _create_table_block(table_data)

    assert table_renderer._get_table_width(block) == 3


@pytest.mark.asyncio
async def test_extract_row_cells_should_convert_cells_to_markdown(
    table_renderer: TableRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    async def mock_to_markdown(rich_text):
        if rich_text and len(rich_text) > 0:
            return rich_text[0].plain_text
        return ""

    mock_rich_text_markdown_converter.to_markdown = AsyncMock(side_effect=mock_to_markdown)

    cells = [
        [RichText.from_plain_text("Cell 1")],
        [RichText.from_plain_text("Cell 2")],
    ]
    row = _create_table_row_block(cells)

    result = await table_renderer._extract_row_cells(row)

    assert result == ["Cell 1", "Cell 2"]


@pytest.mark.asyncio
async def test_minimum_column_width_constant_should_be_correct(
    table_renderer: TableRenderer,
) -> None:
    assert table_renderer.MINIMUM_COLUMN_WIDTH == 3
