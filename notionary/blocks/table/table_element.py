from __future__ import annotations
import re
from typing import Optional

from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_types import BlockType
from notionary.blocks.notion_block_element import NotionBlockElement

from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.table.table_models import (
    CreateTableBlock,
    TableBlock,
)



class TableElement(NotionBlockElement):
    """
    Handles conversion between Markdown tables and Notion table blocks.
    Now integrated into the LineProcessor stack system.

    Markdown table syntax:
    | Header 1 | Header 2 | Header 3 |
    [table rows as child lines]
    """

    # Pattern für Table-Zeilen (jede Zeile die mit | startet und endet)
    ROW_PATTERN = re.compile(r"^\s*\|(.+)\|\s*$")
    # Pattern für Separator-Zeilen
    SEPARATOR_PATTERN = re.compile(r"^\s*\|([\s\-:|]+)\|\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text starts a table (first row with | ... |)."""
        return bool(cls.ROW_PATTERN.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion table."""
        return block.type == BlockType.TABLE and block.table

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert opening table row to Notion table block."""
        if not cls.ROW_PATTERN.match(text.strip()):
            return None

        # Parse the header row to determine column count
        header_cells = cls._parse_table_row(text)
        col_count = len(header_cells)

        # Create empty TableBlock - content will be added by stack processor
        table_block = TableBlock(
            table_width=col_count,
            has_column_header=True,
            has_row_header=False,
            children=[],  # Will be populated by stack processor
        )

        return CreateTableBlock(table=table_block)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion table block to markdown table."""
        if block.type != BlockType.TABLE:
            return None

        if not block.table:
            return None

        table_data = block.table
        children = block.children or []

        if not children:
            table_width = table_data.table_width or 3
            header = (
                "| " + " | ".join([f"Column {i+1}" for i in range(table_width)]) + " |"
            )
            separator = (
                "| " + " | ".join(["--------" for _ in range(table_width)]) + " |"
            )
            data_row = (
                "| " + " | ".join(["        " for _ in range(table_width)]) + " |"
            )
            table_rows = [header, separator, data_row]
            return "\n".join(table_rows)

        table_rows = []
        header_processed = False

        for child in children:
            if child.type != "table_row":
                continue

            if not child.table_row:
                continue

            row_data = child.table_row
            cells = row_data.cells or []

            row_cells = []
            for cell in cells:
                cell_text = TextInlineFormatter.extract_text_with_formatting(cell)
                row_cells.append(cell_text or "")

            row = "| " + " | ".join(row_cells) + " |"
            table_rows.append(row)

            if not header_processed and table_data.has_column_header:
                header_processed = True
                separator = (
                    "| " + " | ".join(["--------" for _ in range(len(cells))]) + " |"
                )
                table_rows.append(separator)

        return "\n".join(table_rows)

    @classmethod
    def _parse_table_row(cls, row_text: str) -> list[str]:
        """Convert table row text to cell contents."""
        row_content = row_text.strip()

        if row_content.startswith("|"):
            row_content = row_content[1:]
        if row_content.endswith("|"):
            row_content = row_content[:-1]

        return [cell.strip() for cell in row_content.split("|")]

    @classmethod
    def is_table_row(cls, line: str) -> bool:
        """Check if a line is a valid table row."""
        return bool(cls.ROW_PATTERN.match(line.strip()))