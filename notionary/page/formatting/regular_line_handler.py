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
        
        # These elements manage their own children via specific handlers
        managed_elements = (ColumnListElement, ColumnElement)
        
        return issubclass(current_parent.element_type, managed_elements)

    def _add_to_parent_context(self, context: LineProcessingContext) -> None:
        """Add line as child to the current parent context."""
        context.parent_stack[-1].add_child_line(context.line)

    def _process_regular_line(self, context: LineProcessingContext) -> bool:
        """Process a regular line and check for parent blocks."""
        for element in context.block_registry.get_elements():
            # Skip elements that are handled by specialized handlers
            if issubclass(element, (ColumnListElement, ColumnElement)):
                continue
                
            # Skip lines that look like column directives  
            if context.line.strip().startswith(":::"):
                continue
                
            if not (result := element.markdown_to_notion(context.line)):
                continue

            blocks = self._normalize_to_list(result)
            if not blocks:
                continue

            for block in blocks:
                if not self._can_have_children(block, element):
                    context.result_blocks.append(block)
                else:
                    child_prefix = self._get_child_prefix(element)
                    parent_context = ParentBlockContext(
                        block=block,
                        element_type=element,
                        child_prefix=child_prefix,
                        child_lines=[],
                    )
                    context.parent_stack.append(parent_context)

            return True

        return False

    def _process_as_paragraph(self, context: LineProcessingContext) -> None:
        """Process a line as a paragraph."""
        result = context.block_registry.markdown_to_notion(context.line)
        if not result:
            return

        blocks = self._normalize_to_list(result)
        for block in blocks:
            context.result_blocks.append(block)

    def _can_have_children(
        self, block: BlockCreateRequest, element: NotionBlockElement
    ) -> bool:
        """Check if a block can have children."""
        from notionary.blocks.code.code_element import CodeElement
        from notionary.blocks.table.table_element import TableElement
        from notionary.blocks.toggle.toggle_element import ToggleElement
        from notionary.blocks.toggleable_heading.toggleable_heading_element import (
            ToggleableHeadingElement,
        )

        parent_elements = (
            CodeElement,
            TableElement,
            ToggleElement,
            ToggleableHeadingElement,  # Only toggleable headings, not regular headings
            # ColumnListElement, ColumnElement removed - handled by specialized handlers
        )

        if issubclass(element, parent_elements):
            return True

        # Check block attributes for children capability - BUT skip regular headings
        attrs_to_check = [
            ("toggle", "children"),
            ("code", "rich_text"),
            ("table", "children"),
            # Removed heading_1, heading_2, heading_3 - regular headings don't need children
            # Only toggleable headings are handled by ToggleableHeadingElement above
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
        parents_to_finalize = []
        
        # Collect unmanaged parents from the top of the stack
        while context.parent_stack:
            current_parent = context.parent_stack[-1]
            
            # If it's a managed element, don't finalize it
            if issubclass(current_parent.element_type, (ColumnListElement, ColumnElement)):
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
        """Assign children to a parent block."""
        attrs_to_check = [
            ("toggle", "children"),
            ("heading_1", "children"),
            ("heading_2", "children"),
            ("heading_3", "children"),
            # column-related removed - handled by specialized handlers
        ]

        for attr1, attr2 in attrs_to_check:
            if hasattr(parent_block, attr1) and hasattr(
                getattr(parent_block, attr1), attr2
            ):
                setattr(getattr(parent_block, attr1), attr2, children)
                return

        if hasattr(parent_block, "children"):
            parent_block.children = children

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalize the result to a list."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]