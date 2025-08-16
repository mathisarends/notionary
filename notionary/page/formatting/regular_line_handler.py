from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.column.column_list_element import ColumnListElement
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.formatting.line_handler import (
    LineHandler,
    LineProcessingContext,
    ParentBlockContext,
)
from notionary.blocks.block_models import BlockCreateRequest, BlockCreateResult


class RegularLineHandler(LineHandler):
    """Handles regular lines - respects parent contexts like columns."""

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return context.line.strip()

    def _process(self, context: LineProcessingContext) -> None:
        # Check if we're inside a parent context (Column/ColumnList/etc.)
        if self._is_in_parent_context(context):
            self._add_to_parent_context(context)
            context.was_processed = True
            context.should_continue = True
            return

        # Only finalize parents if we're NOT in a managed parent context
        self._finalize_unmanaged_parents(context)

        block_created = self._process_regular_line(context)
        if not block_created:
            self._process_as_paragraph(context)

        context.was_processed = True

    def _is_in_parent_context(self, context: LineProcessingContext) -> bool:
        """Check if we're inside a parent context that manages its own children."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]

        # Only Column elements manage their children via RegularLineHandler
        # Toggle elements now manage their own children via specialized handlers
        managed_elements = (ColumnListElement, ColumnElement)

        return issubclass(current_parent.element_type, managed_elements)

    def _add_to_parent_context(self, context: LineProcessingContext) -> None:
        """Add line as child to the current parent context."""
        context.parent_stack[-1].add_child_line(context.line)

    def _process_regular_line(self, context: LineProcessingContext) -> bool:
        """Process a regular line - now only for non-heading, non-toggle, non-column content."""
        # Skip lines that look like any special directives
        line = context.line.strip()
        if line.startswith((":::", "+++", "#")):
            return False

        # Try to create blocks through registry for other special elements (lists, etc.)
        for element in context.block_registry.get_elements():
            # Skip elements that are handled by specialized handlers
            from notionary.blocks.toggle.toggle_element import ToggleElement
            from notionary.blocks.toggleable_heading.toggleable_heading_element import (
                ToggleableHeadingElement,
            )
            from notionary.blocks.heading.heading_element import HeadingElement

            if issubclass(
                element,
                (
                    ColumnListElement,
                    ColumnElement,
                    ToggleElement,
                    ToggleableHeadingElement,
                    HeadingElement,
                ),
            ):
                continue

            if not (result := element.markdown_to_notion(context.line)):
                continue

            blocks = self._normalize_to_list(result)
            if not blocks:
                continue

            for block in blocks:
                # Since we skip most parent elements above, most blocks should go directly to result
                context.result_blocks.append(block)

            return True

        return False

    def _process_as_paragraph(self, context: LineProcessingContext) -> None:
        """Process a line as a simple paragraph - no more complex block types."""
        # Create a simple paragraph block directly
        from notionary.blocks.paragraph.paragraph_element import ParagraphElement

        paragraph_element = ParagraphElement()
        result = paragraph_element.markdown_to_notion(context.line)

        if not result:
            return

        blocks = self._normalize_to_list(result)
        for block in blocks:
            context.result_blocks.append(block)

    def _can_have_children(
        self, block: BlockCreateRequest, element: NotionBlockElement
    ) -> bool:
        """Check if a block can have children - simplified since most parent blocks are handled elsewhere."""
        # Most parent elements are now handled by specialized handlers
        # Only check for basic cases like lists, etc.

        attrs_to_check = [
            ("code", "rich_text"),  # Code blocks still use old system
            ("table", "children"),  # Tables still use old system
        ]

        for attr1, attr2 in attrs_to_check:
            if hasattr(block, attr1) and hasattr(getattr(block, attr1), attr2):
                return True

        return False

    def _get_child_prefix(self, element: NotionBlockElement) -> str:
        """Determine the child prefix for the element type."""
        from notionary.blocks.code.code_element import CodeElement
        from notionary.blocks.table.table_element import TableElement

        if issubclass(element, CodeElement):
            return "RAW"
        elif issubclass(element, TableElement):
            return "TABLE_ROW"
        else:
            return ""  # No prefix for most elements

    def _finalize_unmanaged_parents(self, context: LineProcessingContext) -> None:
        """Finalize only unmanaged parent blocks (not Column/ColumnList)."""
        # Note: Toggle/ToggleableHeading are now managed by their own handlers

        parents_to_finalize = []

        # Collect unmanaged parents from the top of the stack
        while context.parent_stack:
            current_parent = context.parent_stack[-1]

            # If it's a managed element, don't finalize it
            if issubclass(
                current_parent.element_type, (ColumnListElement, ColumnElement)
            ):
                break

            parents_to_finalize.append(context.parent_stack.pop())

        # Process the collected parents
        for parent_context in reversed(parents_to_finalize):
            if parent_context.has_children():
                children_text = "\n".join(parent_context.child_lines)
                children_blocks = self._convert_children_text(
                    children_text, context.block_registry
                )
                self._assign_children(parent_context.block, children_blocks)

            context.result_blocks.append(parent_context.block)

    def _convert_children_text(
        self, text: str, block_registry: BlockRegistry
    ) -> list[BlockCreateRequest]:
        """Recursively convert children text."""
        from notionary.page.formatting.markdown_to_notion_converter import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return child_converter._process_lines(text)

    def _assign_children(
        self, parent_block: BlockCreateRequest, children: list[BlockCreateRequest]
    ) -> None:
        """Assign children to a parent block - simplified."""
        # Most parent blocks are now handled by specialized handlers
        attrs_to_check = [
            ("code", "rich_text"),  # Code blocks
            ("table", "children"),  # Tables
        ]

        for attr1, attr2 in attrs_to_check:
            if hasattr(parent_block, attr1) and hasattr(
                getattr(parent_block, attr1), attr2
            ):
                setattr(getattr(parent_block, attr1), attr2, children)
                return

        # Fallback for any block with a children attribute
        if hasattr(parent_block, "children"):
            parent_block.children = children

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalize the result to a list."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
