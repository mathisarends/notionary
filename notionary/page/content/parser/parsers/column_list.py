from __future__ import annotations

import re

from notionary.blocks.mappings.column_list import ColumnListMapper
from notionary.page.content.parser.context import ParentBlockContext
from notionary.page.content.parser.parsers.base import (
    LineParser,
    LineProcessingContext,
)


class ColumnListParser(LineParser):
    def __init__(self) -> None:
        super().__init__()
        self._start_pattern = re.compile(r"^:::\s*columns?\s*$", re.IGNORECASE)
        self._end_pattern = re.compile(r"^:::\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_column_list_start(context) or self._is_column_list_end(context)

    async def _process(self, context: LineProcessingContext) -> None:
        if self._is_column_list_start(context):
            await self._start_column_list(context)
            return

        if self._is_column_list_end(context):
            await self._finalize_column_list(context)

    def _is_column_list_start(self, context: LineProcessingContext) -> bool:
        """Check if line starts a column list (::: columns)."""
        return self._start_pattern.match(context.line.strip()) is not None

    def _is_column_list_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a column list (:::)."""
        if not self._end_pattern.match(context.line.strip()):
            return False

        if not context.parent_stack:
            return False

        # Check if top of stack is a ColumnList
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ColumnListMapper)

    async def _start_column_list(self, context: LineProcessingContext) -> None:
        """Start a new column list."""
        # Create ColumnList block using the element from registry
        column_list_element = None
        for element in context.block_registry.get_elements():
            if issubclass(element, ColumnListMapper):
                column_list_element = element
                break

        if not column_list_element:
            return

        # Create the block
        result = await column_list_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=column_list_element,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    async def _finalize_column_list(self, context: LineProcessingContext) -> None:
        """Finalize a column list and add it to result_blocks."""
        column_list_context = context.parent_stack.pop()
        await self._assign_column_list_children_if_any(column_list_context, context)

        # Check if we have a parent context to add this column_list to
        if context.parent_stack:
            # Add this column_list as a child block to the parent (like Toggle)
            parent_context = context.parent_stack[-1]
            parent_context.add_child_block(column_list_context.block)

        else:
            # No parent, add to top level
            context.result_blocks.append(column_list_context.block)

    async def _assign_column_list_children_if_any(
        self, column_list_context: ParentBlockContext, context: LineProcessingContext
    ) -> None:
        """Collect and assign any column children blocks inside this column list."""
        all_children = []

        # Process text lines
        if column_list_context.child_lines:
            children_text = "\n".join(column_list_context.child_lines)
            children_blocks = await self._convert_children_text(children_text, context.block_registry)
            all_children.extend(children_blocks)

        if column_list_context.child_blocks:
            all_children.extend(column_list_context.child_blocks)

        # Filter only column blocks
        column_children = [
            block for block in all_children if hasattr(block, "column") and getattr(block, "type", None) == "column"
        ]
        column_list_context.block.column_list.children = column_children

    async def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.content.parser.service import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return await child_converter.process_lines(text)
