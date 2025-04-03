# File: elements/tables.py

from typing import Dict, Any, Optional, List, Tuple
import re
from notionary.converters.notion_block_element import NotionBlockElement
from notionary.converters.elements.text_formatting import extract_text_with_formatting, parse_inline_formatting

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
    
    # Patterns for detecting Markdown tables
    ROW_PATTERN = re.compile(r'^\s*\|(.+)\|\s*$')
    SEPARATOR_PATTERN = re.compile(r'^\s*\|([\s\-:|]+)\|\s*$')
    
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text contains a markdown table."""
        lines = text.split('\n')
        
        if len(lines) < 3:
            return False
        
        for i, line in enumerate(lines[:-2]):
            if (TableElement.ROW_PATTERN.match(line) and 
                TableElement.SEPARATOR_PATTERN.match(lines[i+1]) and 
                TableElement.ROW_PATTERN.match(lines[i+2])):
                return True
                
        return False
    
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion table."""
        return block.get("type") == "table"
    
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown table to Notion table block."""
        if not TableElement.match_markdown(text):
            return None
        
        lines = text.split('\n')
        
        table_start = TableElement._find_table_start(lines)
        if table_start is None:
            return None
        
        table_end = TableElement._find_table_end(lines, table_start)
        table_lines = lines[table_start:table_end]
        
        rows = TableElement._extract_table_rows(table_lines)
        if not rows:
            return None
            
        column_count = len(rows[0])
        TableElement._normalize_row_lengths(rows, column_count)
        
        return {
            "type": "table",
            "table": {
                "table_width": column_count,
                "has_column_header": True,
                "has_row_header": False,
                "children": TableElement._create_table_rows(rows)
            }
        }
    
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion table block to markdown table."""
        if block.get("type") != "table":
            return None
        
        table_data = block.get("table", {})
        children = block.get("children", [])
        
        if not children:
            table_width = table_data.get("table_width", 3)
            
            header = "| " + " | ".join([f"Column {i+1}" for i in range(table_width)]) + " |"
            separator = "| " + " | ".join(["--------" for _ in range(table_width)]) + " |"
            data_row = "| " + " | ".join(["        " for _ in range(table_width)]) + " |"
            
            table_rows = [header, separator, data_row]
            return "\n".join(table_rows)
        
        table_rows = []
        header_processed = False
        
        for child in children:
            if child.get("type") != "table_row":
                continue
                
            row_data = child.get("table_row", {})
            cells = row_data.get("cells", [])
            
            row_cells = []
            for cell in cells:
                cell_text = extract_text_with_formatting(cell)
                row_cells.append(cell_text or "")
            
            row = "| " + " | ".join(row_cells) + " |"
            table_rows.append(row)
            
            if not header_processed and table_data.get("has_column_header", True):
                header_processed = True
                separator = "| " + " | ".join(["--------" for _ in range(len(cells))]) + " |"
                table_rows.append(separator)
        
        if not table_rows:
            return None
            
        if len(table_rows) == 1 and table_data.get("has_column_header", True):
            cells_count = len(children[0].get("table_row", {}).get("cells", []))
            separator = "| " + " | ".join(["--------" for _ in range(cells_count)]) + " |"
            table_rows.insert(1, separator)
            
        return "\n".join(table_rows)
    
    @staticmethod
    def is_multiline() -> bool:
        """Indicates if this element handles content that spans multiple lines."""
        return True
    
    @staticmethod
    def _find_table_start(lines: List[str]) -> Optional[int]:
        """Find the start index of a table in the lines."""
        for i in range(len(lines) - 2):
            if (TableElement.ROW_PATTERN.match(lines[i]) and 
                TableElement.SEPARATOR_PATTERN.match(lines[i+1]) and 
                TableElement.ROW_PATTERN.match(lines[i+2])):
                return i
        return None
    
    @staticmethod
    def _find_table_end(lines: List[str], start_idx: int) -> int:
        """Find the end index of a table, starting from start_idx."""
        end_idx = start_idx + 3  # Minimum: Header, Separator, one data row
        while end_idx < len(lines) and TableElement.ROW_PATTERN.match(lines[end_idx]):
            end_idx += 1
        return end_idx
    
    @staticmethod
    def _extract_table_rows(table_lines: List[str]) -> List[List[str]]:
        """Extract row contents from table lines, excluding separator line."""
        rows = []
        for i, line in enumerate(table_lines):
            if i != 1 and TableElement.ROW_PATTERN.match(line):  # Skip separator line
                cells = TableElement._parse_table_row(line)
                if cells:
                    rows.append(cells)
        return rows
    
    @staticmethod
    def _normalize_row_lengths(rows: List[List[str]], column_count: int) -> None:
        """Normalize row lengths to the specified column count."""
        for row in rows:
            if len(row) < column_count:
                row.extend([""] * (column_count - len(row)))
            elif len(row) > column_count:
                del row[column_count:]
    
    @staticmethod
    def _parse_table_row(row_text: str) -> List[str]:
        """Convert table row text to cell contents."""
        row_content = row_text.strip()
        
        if row_content.startswith('|'):
            row_content = row_content[1:]
        if row_content.endswith('|'):
            row_content = row_content[:-1]
            
        return [cell.strip() for cell in row_content.split('|')]
    
    @staticmethod
    def _create_table_rows(rows: List[List[str]]) -> List[Dict[str, Any]]:
        """Create Notion table rows from cell contents."""
        table_rows = []
        
        for row in rows:
            cells_data = []
            
            for cell_content in row:
                rich_text = parse_inline_formatting(cell_content)
                
                if not rich_text:
                    rich_text = [{
                        "type": "text",
                        "text": {"content": ""},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                        },
                        "plain_text": "",
                        "href": None
                    }]
                    
                cells_data.append(rich_text)
                
            table_rows.append({
                "type": "table_row",
                "table_row": {
                    "cells": cells_data
                }
            })
            
        return table_rows
    
    @staticmethod
    def find_matches(text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all tables in the text and return their positions.
        
        Args:
            text: The text to search in
            
        Returns:
            List of tuples with (start_pos, end_pos, block)
        """
        matches = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines) - 2:
            if (TableElement.ROW_PATTERN.match(lines[i]) and 
                TableElement.SEPARATOR_PATTERN.match(lines[i+1]) and 
                TableElement.ROW_PATTERN.match(lines[i+2])):
                
                start_line = i
                end_line = TableElement._find_table_end(lines, start_line)
                
                start_pos = TableElement._calculate_position(lines, 0, start_line)
                end_pos = start_pos + TableElement._calculate_position(lines, start_line, end_line)
                
                table_text = '\n'.join(lines[start_line:end_line])
                table_block = TableElement.markdown_to_notion(table_text)
                
                if table_block:
                    matches.append((start_pos, end_pos, table_block))
                
                i = end_line
            else:
                i += 1
                
        return matches
    
    @staticmethod
    def _calculate_position(lines: List[str], start: int, end: int) -> int:
        """Calculate the text position in characters from line start to end."""
        position = 0
        for i in range(start, end):
            position += len(lines[i]) + 1  # +1 for newline
        return position