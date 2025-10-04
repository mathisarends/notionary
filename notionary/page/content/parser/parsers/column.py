import re

from notionary.blocks.mappings.column import ColumnMapper
from notionary.page.content.parser.context import ParentBlockContext
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class ColumnParser(LineParser):
    def __init__(self) -> None:
        super().__init__()
        self._start_pattern = re.compile(r"^:::\s*column(\s+.*?)?\s*$", re.IGNORECASE)
        self._end_pattern = re.compile(r"^:::\s*$")

    def _can_handle(self, context: BlockParsingContext) -> bool:
        return self._is_column_start(context) or self._is_column_end(context)

    async def _process(self, context: BlockParsingContext) -> None:
        if self._is_column_start(context):
            await self._start_column(context)
            return

        if self._is_column_end(context):
            await self._finalize_column(context)

    def _is_column_start(self, context: BlockParsingContext) -> bool:
        """Check if line starts a column (::: column)."""
        return self._start_pattern.match(context.line.strip()) is not None

    def _is_column_end(self, context: BlockParsingContext) -> bool:
        """Check if we need to end a single column (:::)."""
        if not self._end_pattern.match(context.line.strip()):
            return False

        if not context.parent_stack:
            return False

        # Check if top of stack is a Column (not ColumnList)
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ColumnMapper)

    async def _start_column(self, context: BlockParsingContext) -> None:
        """Start a new column."""
        # Create Column block directly - much more efficient!
        column_element = ColumnMapper()
        result = await column_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=ColumnMapper,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    async def _finalize_column(self, context: BlockParsingContext) -> None:
        """Finalize a single column and add it to the column list or result."""
        column_context = context.parent_stack.pop()
        await self._assign_column_children_if_any(column_context, context)

        if context.parent_stack:
            parent = context.parent_stack[-1]
            from notionary.blocks.mappings.column_list import ColumnListMapper

            if issubclass(parent.element_type, ColumnListMapper):
                # Add to parent using the new system
                parent.add_child_block(column_context.block)
                return

        # Fallback: no parent or parent is not ColumnList
        context.result_blocks.append(column_context.block)

    async def _assign_column_children_if_any(
        self, column_context: ParentBlockContext, context: BlockParsingContext
    ) -> None:
        """Collect and assign any children blocks inside this column."""
        all_children = []

        # Process text lines
        if column_context.child_lines:
            children_text = "\n".join(column_context.child_lines)
            text_blocks = await self._convert_children_text(children_text, context.block_registry)
            all_children.extend(text_blocks)

        # Add direct child blocks (like processed toggles)
        if column_context.child_blocks:
            all_children.extend(column_context.child_blocks)

        column_context.block.column.children = all_children

    def _try_add_to_parent_column_list(self, column_context: ParentBlockContext, context: BlockParsingContext) -> bool:
        """If the previous stack element is a ColumnList, append column and return True."""
        if not context.parent_stack:
            return False

        parent = context.parent_stack[-1]
        from notionary.blocks.mappings.column_list import ColumnListMapper

        if not issubclass(parent.element_type, ColumnListMapper):
            return False

        parent.block.column_list.children.append(column_context.block)
        return True

    async def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.content.parser.service import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return await child_converter.process_lines(text)
