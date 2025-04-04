import re
from typing import Dict, Any, Optional, List, Tuple

from notionary.converters.notion_block_element import NotionBlockElement


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
    
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text starts a columns block."""
        return bool(ColumnElement.COLUMNS_START.match(text.strip()))
    
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion column_list."""
        return block.get("type") == "column_list"
    
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
                
                # Process children of this column
                for child_block in column_block.get("column", {}).get("children", []):
                    # This would need to be handled by a full converter
                    result.append("  [Column content]")  # Placeholder
                
                result.append(":::")
        
        # End the columns block
        result.append(":::")
        
        return "\n".join(result)
    
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
            line = lines[i].strip()
            
            # Check for columns start
            if ColumnElement.COLUMNS_START.match(line):
                columns_start = i
                columns_block = ColumnElement.markdown_to_notion(line)
                columns_children = []
                
                # Process columns until we find the end
                column_content = []
                in_column = False
                i += 1
                
                while i < len(lines) and not ColumnElement.COLUMNS_START.match(lines[i].strip()):
                    current_line = lines[i].strip()
                    
                    # Check for column start
                    if ColumnElement.COLUMN_START.match(current_line):
                        # If we were already in a column, finalize it
                        if in_column and column_content:
                            # Process column content recursively
                            from notionary.converters import MarkdownToNotionConverter
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
                            column_content = []
                        
                        in_column = True
                    # Check for block end (only if we're in a column)
                    elif ColumnElement.BLOCK_END.match(current_line) and in_column:
                        # Finalize current column
                        if column_content:
                            # Process column content recursively
                            from notionary.converters import MarkdownToNotionConverter
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
                            column_content = []
                        
                        in_column = False
                    # Check for columns end
                    elif ColumnElement.BLOCK_END.match(current_line) and not in_column:
                        # End of columns block
                        break
                    # Regular content line (if in a column)
                    elif in_column:
                        column_content.append(lines[i])
                    
                    i += 1
                
                # Finalize any remaining column
                if in_column and column_content:
                    # Process column content recursively
                    from notionary.converters import MarkdownToNotionConverter
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
                
                # Add columns to the main block
                if columns_children:
                    columns_block["column_list"]["children"] = columns_children
                
                # Calculate positions
                start_pos = sum(len(lines[j]) + 1 for j in range(columns_start))
                end_pos = sum(len(lines[j]) + 1 for j in range(i + 1))
                
                matches.append((start_pos, end_pos, columns_block))
                
                # Skip to the next line after the columns block
                i += 1
            else:
                i += 1
        
        return matches