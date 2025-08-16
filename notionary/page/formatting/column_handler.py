from __future__ import annotations
import re

from notionary.blocks.column.column_element import ColumnElement
from notionary.page.formatting.line_handler import (
    LineHandler,
    LineProcessingContext,
    ParentBlockContext,
)


class ColumnHandler(LineHandler):
    """Handles single column elements - both start and end."""

    def __init__(self):
        super().__init__()
        # ✅ Allow parameters after 'column' (like widths, classes, etc.)
        self._start_pattern = re.compile(r"^:::\s*column(\s+.*?)?\s*$", re.IGNORECASE)
        self._end_pattern = re.compile(r"^:::\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_column_start(context) or self._is_column_end(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_column_start(context):
            self._start_column(context)
            context.was_processed = True
            context.should_continue = True
            return

        if self._is_column_end(context):
            self._finalize_column(context)
            context.was_processed = True
            context.should_continue = True

    def _is_column_start(self, context: LineProcessingContext) -> bool:
        """Check if line starts a column (::: column)."""
        return self._start_pattern.match(context.line.strip()) is not None

    def _is_column_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a single column (:::)."""
        if not self._end_pattern.match(context.line.strip()):
            return False

        if not context.parent_stack:
            return False

        # Check if top of stack is a Column (not ColumnList)
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ColumnElement)

    def _start_column(self, context: LineProcessingContext) -> None:
        """Start a new column."""
        # Create Column block using the element from registry
        column_element = None
        for element in context.block_registry.get_elements():
            if issubclass(element, ColumnElement):
                column_element = element
                break

        if not column_element:
            return

        # Create the block
        result = column_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result if not isinstance(result, list) else result[0]

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=column_element,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    def _finalize_column(self, context: LineProcessingContext) -> None:
        """Finalize a single column and add it to the column list."""
        column_context = context.parent_stack.pop()

        if column_context.has_children():
            children_text = "\n".join(column_context.child_lines)
            children_blocks = self._convert_children_text(
                children_text, context.block_registry
            )
            # ✅ Column should contain ANY blocks (headings, paragraphs, etc.)
            # NOT just column blocks!
            column_context.block.column.children = children_blocks

        # Add finished column to the column list (which should be next on stack)
        if context.parent_stack and hasattr(context.parent_stack[-1], "element_type"):
            from notionary.blocks.column.column_list_element import ColumnListElement

            if issubclass(context.parent_stack[-1].element_type, ColumnListElement):
                context.parent_stack[-1].block.column_list.children.append(
                    column_context.block
                )
                return

        # Fallback: add to result_blocks if no column list parent
        context.result_blocks.append(column_context.block)

    def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.formatting.markdown_to_notion_converter import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return child_converter._process_lines(text)
