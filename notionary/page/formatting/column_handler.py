from __future__ import annotations
import re

from notionary.blocks.column.column_list_element import ColumnListElement
from notionary.blocks.column.column_element import ColumnElement
from notionary.page.formatting.line_handler import LineHandler, LineProcessingContext


class ColumnHandler(LineHandler):
    """Handles column-specific logic including nested column structures."""

    def __init__(self):
        super().__init__()
        self._end_pattern = re.compile(r"^:::\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return (
            self._is_column_end(context)
            or self._is_column_list_end(context) 
            or self._is_in_column_context(context)
        )

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_column_end(context):
            self._finalize_column(context)
            context.was_processed = True
            context.should_continue = True
            return

        if self._is_column_list_end(context):
            self._finalize_column_list(context)
            context.was_processed = True
            context.should_continue = True
            return

        # Handle content inside columns (| prefix)
        if self._is_in_column_context(context):
            self._add_column_content(context)
            context.was_processed = True
            context.should_continue = True

    def _is_column_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a single column."""
        if not self._end_pattern.match(context.line.strip()):
            return False
        
        if not context.parent_stack:
            return False

        # Check if top of stack is a Column (not ColumnList)
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ColumnElement)

    def _is_column_list_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a column list."""
        if not self._end_pattern.match(context.line.strip()):
            return False
        
        if not context.parent_stack:
            return False

        # Check if top of stack is a ColumnList
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ColumnListElement)

    def _is_in_column_context(self, context: LineProcessingContext) -> bool:
        """Check if we're inside a column and line has | prefix."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not issubclass(current_parent.element_type, (ColumnListElement, ColumnElement)):
            return False

        # Check for | prefix
        return context.line.startswith("|")

    def _finalize_column(self, context: LineProcessingContext) -> None:
        """Finalize a single column and add it to the column list."""
        column_context = context.parent_stack.pop()
        
        if column_context.has_children():
            children_text = "\n".join(column_context.child_lines)
            children_blocks = self._convert_children_text(children_text, context.block_registry)
            column_context.block.column.children = children_blocks

        # Add finished column to the column list (which should be next on stack)
        if context.parent_stack and issubclass(context.parent_stack[-1].element_type, ColumnListElement):
            context.parent_stack[-1].block.column_list.children.append(column_context.block)
        else:
            # Fallback: add to result_blocks if no column list parent
            context.result_blocks.append(column_context.block)

    def _finalize_column_list(self, context: LineProcessingContext) -> None:
        """Finalize a column list."""
        column_list_context = context.parent_stack.pop()
        
        if column_list_context.has_children():
            children_text = "\n".join(column_list_context.child_lines)
            children_blocks = self._convert_children_text(children_text, context.block_registry)
            
            # Filter only column blocks
            column_children = [
                block for block in children_blocks
                if hasattr(block, "column") and getattr(block, "type", None) == "column"
            ]
            column_list_context.block.column_list.children = column_children

        context.result_blocks.append(column_list_context.block)

    def _add_column_content(self, context: LineProcessingContext) -> None:
        """Add content to the current column context."""
        # Remove | prefix and add to child_lines
        if context.line.startswith("| "):
            content = context.line[2:]  # Remove "| "
        elif context.line.startswith("|"):
            content = context.line[1:]  # Remove "|"
        else:
            content = context.line

        context.parent_stack[-1].add_child_line(content)

    def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.formatting.markdown_to_notion_converter import MarkdownToNotionConverter
        
        if not text.strip():
            return []
        
        child_converter = MarkdownToNotionConverter(block_registry)
        return child_converter._process_lines(text)
