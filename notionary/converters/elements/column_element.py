import re
from typing import Dict, Any, Optional, List, Tuple
from typing_extensions import override

from notionary.converters.elements.notion_block_element import NotionBlockElement
from notionary.converters import MarkdownToNotionConverter

class ColumnElement(NotionBlockElement):
    """
    Handles conversion between custom Markdown column syntax and Notion column blocks.
    
    Markdown column syntax:
    ::: columns
    ::: column
    Content for first column
    :::
    ::: column
    Content for second column
    :::
    :::
    
    This creates a column layout in Notion with the specified content in each column.
    """
    
    COLUMNS_START = re.compile(r'^:::\s*columns\s*$')
    COLUMN_START = re.compile(r'^:::\s*column\s*$')
    BLOCK_END = re.compile(r'^:::\s*$')
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text starts a columns block."""
        return bool(ColumnElement.COLUMNS_START.match(text.strip()))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion column_list."""
        return block.get("type") == "column_list"
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """
        Convert markdown column syntax to Notion column blocks.
        
        Note: This only processes the first line (columns start).
        The full column content needs to be processed separately.
        """
        if not ColumnElement.COLUMNS_START.match(text.strip()):
            return None
            
        # Create an empty column_list block
        # Child columns will be added by the column processor
        return {
            "type": "column_list",
            "column_list": {
                "children": []
            }
        }
        
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion column_list block to markdown column syntax."""
        if block.get("type") != "column_list":
            return None
            
        column_children = block.get("column_list", {}).get("children", [])
        
        # Start the columns block
        result = ["::: columns"]
        
        # Process each column
        for column_block in column_children:
            if column_block.get("type") == "column":
                result.append("::: column")
                
            for _ in column_block.get("column", {}).get("children", []):
                result.append("  [Column content]")  # Placeholder
                
                result.append(":::")
        
        # End the columns block
        result.append(":::")
        
        return "\n".join(result)
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        """Column blocks span multiple lines."""
        return True
    
    @staticmethod
    def find_matches(text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all column block matches in the text and return their positions and blocks.
        
        Args:
            text: The input markdown text
            
        Returns:
            List of tuples (start_pos, end_pos, block)
        """
        matches = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            # Skip non-column lines
            if not ColumnElement.COLUMNS_START.match(lines[i].strip()):
                i += 1
                continue
                
            # Process a column block and add to matches
            column_block_info = ColumnElement._process_column_block(lines, i)
            matches.append(column_block_info)
            
            # Skip to the end of the processed column block
            i = column_block_info[3]  # i is returned as the 4th element in the tuple
        
        return [(start, end, block) for start, end, block, _ in matches]

    @staticmethod
    def _process_column_block(lines: List[str], start_index: int) -> Tuple[int, int, Dict[str, Any], int]:
        """
        Process a complete column block structure from the given starting line.
        
        Args:
            lines: All lines of the text
            start_index: Index of the column block start line
            
        Returns:
            Tuple of (start_pos, end_pos, block, next_line_index)
        """
        columns_start = start_index
        columns_block = ColumnElement.markdown_to_notion(lines[start_index].strip())
        columns_children = []
        
        next_index = ColumnElement._collect_columns(lines, start_index + 1, columns_children)
        
        # Add columns to the main block
        if columns_children:
            columns_block["column_list"]["children"] = columns_children
        
        # Calculate positions
        start_pos = sum(len(lines[j]) + 1 for j in range(columns_start))
        end_pos = sum(len(lines[j]) + 1 for j in range(next_index))
        
        return (start_pos, end_pos, columns_block, next_index)

    @staticmethod
    def _collect_columns(lines: List[str], start_index: int, columns_children: List[Dict[str, Any]]) -> int:
        """
        Collect all columns within a column block structure.
        
        Args:
            lines: All lines of the text
            start_index: Index to start collecting from
            columns_children: List to append collected columns to
            
        Returns:
            Next line index after all columns have been processed
        """
        i = start_index
        in_column = False
        column_content = []
        
        while i < len(lines):
            current_line = lines[i].strip()
            
            # Check for nested column block (would be an error, but avoid infinite loop)
            if ColumnElement.COLUMNS_START.match(current_line):
                break
                
            # Process column start
            if ColumnElement.COLUMN_START.match(current_line):
                ColumnElement._finalize_column(column_content, columns_children, in_column)
                column_content = []
                in_column = True
                i += 1
                continue
                
            # Process column end
            if ColumnElement.BLOCK_END.match(current_line) and in_column:
                ColumnElement._finalize_column(column_content, columns_children, in_column)
                column_content = []
                in_column = False
                i += 1
                continue
                
            # Process columns block end
            if ColumnElement.BLOCK_END.match(current_line) and not in_column:
                i += 1
                break
                
            # Regular content line (if in a column)
            if in_column:
                column_content.append(lines[i])
            
            i += 1
        
        # Finalize any remaining column
        ColumnElement._finalize_column(column_content, columns_children, in_column)
        
        return i

    @staticmethod
    def _finalize_column(column_content: List[str], columns_children: List[Dict[str, Any]], in_column: bool) -> None:
        """
        Finalize a column by processing its content and adding it to the columns_children list.
        
        Args:
            column_content: Content lines of the column
            columns_children: List to append the column block to
            in_column: Whether we're currently in a column (if False, does nothing)
        """
        if not (in_column and column_content):
            return
            
        # Process column content recursively
        converter = MarkdownToNotionConverter()
        column_blocks = converter.convert('\n'.join(column_content))
        
        # Create column block
        column_block = {
            "type": "column",
            "column": {
                "children": column_blocks
            }
        }
        columns_children.append(column_block)
        
    @classmethod
    def get_llm_prompt_content(cls) -> dict:
        """
        Returns a dictionary with all information needed for LLM prompts about this element.
        Includes description, usage guidance, syntax options, and examples.
        """
        return {
            "description": "Creates a multi-column layout that displays content side by side.",
            "when_to_use": "Use columns sparingly, only for direct comparisons or when parallel presentation significantly improves readability. Best for pros/cons lists, feature comparisons, or pairing images with descriptions. Avoid overusing as it can complicate document structure.",
            "syntax": [
                "::: columns",
                "::: column",
                "Content for first column",
                ":::",
                "::: column",
                "Content for second column",
                ":::",
                ":::"
            ],
            "notes": [
                "Any Notion block can be placed within columns",
                "Add more columns with additional '::: column' sections",
                "Each column must close with ':::' and the entire columns section with another ':::'"
            ],
            "examples": [
                "::: columns\n::: column\n## Features\n- Fast response time\n- Intuitive interface\n- Regular updates\n:::\n::: column\n## Benefits\n- Increased productivity\n- Better collaboration\n- Simplified workflows\n:::\n:::",
                
                "::: columns\n::: column\n![Image placeholder](/api/placeholder/400/320)\n:::\n::: column\nThis text appears next to the image, creating a media-with-caption style layout that's perfect for documentation or articles.\n:::\n:::"
            ]
        }