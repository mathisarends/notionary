from __future__ import annotations

import re

from notionary.blocks.column.column_element import ColumnElement
from notionary.page.writer.handler.line_handler import (LineHandler,
                                                        LineProcessingContext)
from notionary.page.writer.handler.line_processing_context import \
    ParentBlockContext


class ColumnHandler(LineHandler):
    """Handles single column elements - both start and end.
    Syntax:
    ::: column      # Start individual column (can have optional parameters)
    Content here
    :::             # End column
    """

    def __init__(self):
        super().__init__()
        self._start_pattern = re.compile(r"^:::\s*column(\s+.*?)?\s*$", re.IGNORECASE)
        self._end_pattern = re.compile(r"^:::\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_column_start(context) or self._is_column_end(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_column_start(context):
            self._start_column(context)
            self._mark_processed(context)
            return

        if self._is_column_end(context):
            self._finalize_column(context)
            self._mark_processed(context)

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
        # Create Column block directly - much more efficient!
        column_element = ColumnElement()
        result = column_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=ColumnElement,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    def _finalize_column(self, context: LineProcessingContext) -> None:
        """Finalize a single column and add it to the column list or result."""
        column_context = context.parent_stack.pop()
        self._assign_column_children_if_any(column_context, context)

        if context.parent_stack:
            parent = context.parent_stack[-1]
            from notionary.blocks.column.column_list_element import \
                ColumnListElement

            if issubclass(parent.element_type, ColumnListElement):
                # Add to parent using the new system
                parent.add_child_block(column_context.block)
                return

        # Fallback: no parent or parent is not ColumnList
        context.result_blocks.append(column_context.block)

    def _assign_column_children_if_any(
        self, column_context: ParentBlockContext, context: LineProcessingContext
    ) -> None:
        """Collect and assign any children blocks inside this column."""
        all_children = []

        # Process text lines
        if column_context.child_lines:
            children_text = "\n".join(column_context.child_lines)
            text_blocks = self._convert_children_text(
                children_text, context.block_registry
            )
            all_children.extend(text_blocks)

        # Add direct child blocks (like processed toggles)
        if column_context.child_blocks:
            all_children.extend(column_context.child_blocks)

        column_context.block.column.children = all_children

    def _try_add_to_parent_column_list(
        self, column_context: ParentBlockContext, context: LineProcessingContext
    ) -> bool:
        """If the previous stack element is a ColumnList, append column and return True."""
        if not context.parent_stack:
            return False

        parent = context.parent_stack[-1]
        from notionary.blocks.column.column_list_element import \
            ColumnListElement

        if not issubclass(parent.element_type, ColumnListElement):
            return False

        parent.block.column_list.children.append(column_context.block)
        return True

    def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.writer.markdown_to_notion_converter import \
            MarkdownToNotionConverter

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return child_converter._process_lines(text)

    def _mark_processed(self, context: LineProcessingContext) -> None:
        """Mark context as processed and signal to continue."""
        context.was_processed = True
        context.should_continue = True
