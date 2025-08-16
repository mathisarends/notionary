from __future__ import annotations
import re

from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.column.column_list_element import ColumnListElement
from notionary.page.formatting.line_handler import LineHandler, LineProcessingContext


class ChildContentHandler(LineHandler):
    """Handles child content with prefix logic - but respects column handlers."""

    def _can_handle(self, context: LineProcessingContext) -> bool:
        if not context.parent_stack:
            return False

        # Skip if we're in column context - RegularLineHandler handles this
        if self._is_in_column_context(context):
            return False

        return self._matches_child_pattern(context)

    def _process(self, context: LineProcessingContext) -> None:
        current_parent = context.parent_stack[-1]
        child_prefix = current_parent.child_prefix

        # Standard prefix logic for non-column elements
        child_pattern = re.compile(rf"^{re.escape(child_prefix)}\s?(.*?)$")
        match = child_pattern.match(context.line)
        if not match:
            return

        child_content = match.group(1)
        current_parent.add_child_line(child_content)
        context.was_processed = True
        context.should_continue = True

    def _is_in_column_context(self, context: LineProcessingContext) -> bool:
        """Check if we're inside a column context that RegularLineHandler should handle."""
        current_parent = context.parent_stack[-1]
        return issubclass(
            current_parent.element_type, (ColumnListElement, ColumnElement)
        )

    def _matches_child_pattern(self, context: LineProcessingContext) -> bool:
        """Check if line matches the child pattern for current parent."""
        current_parent = context.parent_stack[-1]
        child_prefix = current_parent.child_prefix

        # Skip RAW and TABLE_ROW as they're handled by specialized handlers
        if child_prefix in ["RAW", "TABLE_ROW", ""]:  # Added "" for column elements
            return False

        child_pattern = re.compile(rf"^{re.escape(child_prefix)}\s?(.*?)$")
        return child_pattern.match(context.line) is not None
