from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.column.column_list_element import ColumnListElement
from notionary.page.writer.handler import (
    LineHandler,
    LineProcessingContext,
)
from notionary.blocks.models import BlockCreateRequest, BlockCreateResult


class RegularLineHandler(LineHandler):
    """Handles regular lines - respects parent contexts like columns."""

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return context.line.strip()

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_in_column_context(context):
            self._add_to_column_context(context)
            context.was_processed = True
            context.should_continue = True
            return

        block_created = self._process_single_line_content(context)
        if not block_created:
            self._process_as_paragraph(context)

        context.was_processed = True

    def _is_in_column_context(self, context: LineProcessingContext) -> bool:
        """Check if we're inside a Column/ColumnList context."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return issubclass(
            current_parent.element_type, (ColumnListElement, ColumnElement)
        )

    def _add_to_column_context(self, context: LineProcessingContext) -> None:
        """Add line as child to the current Column context."""
        context.parent_stack[-1].add_child_line(context.line)

    def _process_single_line_content(self, context: LineProcessingContext) -> bool:
        """Process a regular line for simple elements (lists, etc.)."""
        for element in context.block_registry.get_elements():
            # Skip all elements that have specialized handlers
            from notionary.blocks.toggle import ToggleElement
            from notionary.blocks.toggleable_heading import (
                ToggleableHeadingElement,
            )
            from notionary.blocks.table import TableElement
            from notionary.blocks.code import CodeElement
            from notionary.blocks.paragraph import ParagraphElement
            
            specialized_elements = (
                ColumnListElement,
                ColumnElement,
                ToggleElement,
                ToggleableHeadingElement,
                TableElement,
                CodeElement,
                ParagraphElement,  # Skip paragraph to ensure equations are processed first
            )

            if issubclass(element, specialized_elements):
                continue

            result = element.markdown_to_notion(context.line)
            if not result:
                continue

            blocks = self._normalize_to_list(result)
            for block in blocks:
                context.result_blocks.append(block)

            return True

        return False

    def _process_as_paragraph(self, context: LineProcessingContext) -> None:
        """Process a line as a paragraph."""
        from notionary.blocks.paragraph.paragraph_element import ParagraphElement

        paragraph_element = ParagraphElement()
        result = paragraph_element.markdown_to_notion(context.line)

        if result:
            blocks = self._normalize_to_list(result)
            for block in blocks:
                context.result_blocks.append(block)

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalize the result to a list."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
