import re
from typing import Optional, Any, Tuple

from notionary.blocks.block_models import (
    Block,
)
from notionary.blocks.notion_block_element import BlockCreateResult, NotionBlockElement
from notionary.blocks.paragraph.paragraph_models import CreateParagraphBlock, ParagraphBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.table.table_models import CreateTableBlock, CreateTableRowBlock, TableBlock, TableRowBlock
from notionary.prompts import ElementPromptBuilder, ElementPromptContent

class TableElement(NotionBlockElement):
    """
    Handles conversion between Markdown tables and Notion table blocks.

    Markdown table syntax:
    | Header 1 | Header 2 | Header 3 |
    | -------- | -------- | -------- |
    | Cell 1   | Cell 2   | Cell 3   |
    | Cell 4   | Cell 5   | Cell 6   |

    The second line with dashes and optional colons defines column alignment.
    """

    ROW_PATTERN = re.compile(r"^\s*\|(.+)\|\s*$")
    SEPARATOR_PATTERN = re.compile(r"^\s*\|([\s\-:|]+)\|\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """
        Check if text contains a markdown table.
        Accepts tables with only header + separator, as well as header + separator + data rows.
        """
        lines = text.split("\n")

        if len(lines) < 2:
            return False

        # Akzeptiere Header + Separator auch ohne Datenzeile
        for i, line in enumerate(lines[:-1]):
            if cls.ROW_PATTERN.match(line) and cls.SEPARATOR_PATTERN.match(
                lines[i + 1]
            ):
                return True

        return False

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion table."""
        return block.type == "table"

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown table to Notion TableBlock with rows, followed by an empty paragraph."""
        # Only process if it's a markdown table
        if not cls.PATTERN.match(text.strip()):
            return None

        lines = text.split("\n")
        # Find header separator (e.g., | --- | --- |)
        try:
            sep_index = next(
                i
                for i, line in enumerate(lines)
                if re.match(r"^\|?(?:\s*-+\s*\|)+$", line)
            )
        except StopIteration:
            return None

        header_line = lines[0]
        body_lines = lines[sep_index + 1 :]

        headers = [cell.strip() for cell in header_line.strip("|").split("|")]
        rows_data = []  # type: List[List[str]]
        for line in body_lines:
            if not line.strip().startswith("|"):
                break
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            rows_data.append(cells)

        if not rows_data:
            return None

        # Build TableBlock
        col_count = len(headers)
        table_block = TableBlock(
            table_width=col_count, has_column_header=True, has_row_header=False
        )

        # Build table rows
        table_rows = []
        # First header row
        header_row = TableRowBlock(
            cells=[[RichTextObject.from_plain_text(h)] for h in headers]
        )
        table_rows.append(CreateTableRowBlock(table_row=header_row))

        # Body rows
        for row in rows_data:
            # normalize row length
            if len(row) < col_count:
                row += [""] * (col_count - len(row))
            row_cells = [[RichTextObject.from_plain_text(cell)] for cell in row]
            table_rows.append(
                CreateTableRowBlock(table_row=TableRowBlock(cells=row_cells))
            )

        # Empty paragraph after table
        empty_para = ParagraphBlock(rich_text=[])

        return [
            CreateTableBlock(table=table_block),
            *table_rows,
            CreateParagraphBlock(paragraph=empty_para),
        ]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion table block to markdown table."""
        if block.type != "table":
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

        if not table_rows:
            return None

        if len(table_rows) == 1 and table_data.has_column_header:
            if children and children[0].table_row:
                cells_count = len(children[0].table_row.cells or [])
                separator = (
                    "| " + " | ".join(["--------" for _ in range(cells_count)]) + " |"
                )
                table_rows.insert(1, separator)

        return "\n".join(table_rows)

    @classmethod
    def is_multiline(cls) -> bool:
        """Indicates if this element handles content that spans multiple lines."""
        return True

    @classmethod
    def _find_table_start(cls, lines: list[str]) -> Optional[int]:
        """Find the start index of a table in the lines."""
        for i in range(len(lines) - 2):
            if (
                TableElement.ROW_PATTERN.match(lines[i])
                and TableElement.SEPARATOR_PATTERN.match(lines[i + 1])
                and TableElement.ROW_PATTERN.match(lines[i + 2])
            ):
                return i
        return None

    @classmethod
    def _find_table_end(cls, lines: list[str], start_idx: int) -> int:
        """Find the end index of a table, starting from start_idx."""
        end_idx = start_idx + 3  # Minimum: Header, Separator, one data row
        while end_idx < len(lines) and TableElement.ROW_PATTERN.match(lines[end_idx]):
            end_idx += 1
        return end_idx

    @classmethod
    def _extract_table_rows(cls, table_lines: list[str]) -> list[list[str]]:
        """Extract row contents from table lines, excluding separator line."""
        rows = []
        for i, line in enumerate(table_lines):
            if i != 1 and TableElement.ROW_PATTERN.match(line):  # Skip separator line
                cells = TableElement._parse_table_row(line)
                if cells:
                    rows.append(cells)
        return rows

    @classmethod
    def _normalize_row_lengths(cls, rows: list[list[str]], column_count: int) -> None:
        """Normalize row lengths to the specified column count."""
        for row in rows:
            if len(row) < column_count:
                row.extend([""] * (column_count - len(row)))
            elif len(row) > column_count:
                del row[column_count:]

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
    def _create_table_rows(cls, rows: list[list[str]]) -> list[dict[str, Any]]:
        """Create Notion table rows from cell contents."""
        table_rows = []

        for row in rows:
            cells_data = []

            for cell_content in row:
                rich_text = TextInlineFormatter.parse_inline_formatting(cell_content)

                if not rich_text:
                    rich_text = [
                        {
                            "type": "text",
                            "text": {"content": ""},
                            "annotations": {
                                "bold": False,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "",
                            "href": None,
                        }
                    ]

                cells_data.append(rich_text)

            table_rows.append({"type": "table_row", "table_row": {"cells": cells_data}})

        return table_rows

    @classmethod
    def find_matches(cls, text: str) -> list[Tuple[int, int, dict[str, Any]]]:
        """
        Find all tables in the text and return their positions.

        Args:
            text: The text to search in

        Returns:
            List of tuples with (start_pos, end_pos, block)
        """
        matches = []
        lines = text.split("\n")

        i = 0
        while i < len(lines) - 2:
            if (
                TableElement.ROW_PATTERN.match(lines[i])
                and TableElement.SEPARATOR_PATTERN.match(lines[i + 1])
                and TableElement.ROW_PATTERN.match(lines[i + 2])
            ):

                start_line = i
                end_line = TableElement._find_table_end(lines, start_line)

                start_pos = TableElement._calculate_position(lines, 0, start_line)
                end_pos = start_pos + TableElement._calculate_position(
                    lines, start_line, end_line
                )

                table_text = "\n".join(lines[start_line:end_line])
                table_block = TableElement.markdown_to_notion(table_text)

                if table_block:
                    matches.append((start_pos, end_pos, table_block))

                i = end_line
            else:
                i += 1

        return matches

    @classmethod
    def _calculate_position(cls, lines: list[str], start: int, end: int) -> int:
        """Calculate the text position in characters from line start to end."""
        position = 0
        for i in range(start, end):
            position += len(lines[i]) + 1  # +1 for newline
        return position

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns information for LLM prompts about this element."""
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates formatted tables with rows and columns for structured data."
            )
            .with_usage_guidelines(
                "Use tables to organize and present structured data in a grid format, making information easier to compare and analyze. Tables are ideal for data sets, comparison charts, pricing information, or any content that benefits from columnar organization."
            )
            .with_syntax(
                "| Header 1 | Header 2 | Header 3 |\n| -------- | -------- | -------- |\n| Cell 1   | Cell 2   | Cell 3   |"
            )
            .with_examples(
                [
                    "| Product | Price | Stock |\n| ------- | ----- | ----- |\n| Widget A | $10.99 | 42 |\n| Widget B | $14.99 | 27 |",
                    "| Name | Role | Department |\n| ---- | ---- | ---------- |\n| John Smith | Manager | Marketing |\n| Jane Doe | Director | Sales |",
                ]
            )
            .build()
        )
