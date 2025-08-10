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
    """Handles regular lines (creating new blocks) - cleaned up without toggle-specific logic."""

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return context.line.strip()

    def _process(self, context: LineProcessingContext) -> None:
        self._finalize_open_parents(context)

        block_created = self._process_regular_line(context)
        if not block_created:
            self._process_as_paragraph(context)

        context.was_processed = True

    def _process_regular_line(self, context: LineProcessingContext) -> bool:
        """Process a regular line and check for parent blocks."""
        for element in context.block_registry.get_elements():
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
            ToggleableHeadingElement,
            ColumnListElement,
            ColumnElement,
        )

        if issubclass(element, parent_elements):
            return True

        # Check block attributes for children capability
        attrs_to_check = [
            ("toggle", "children"),
            ("column_list", "children"),
            ("column", "children"),
            ("code", "rich_text"),
            ("table", "children"),
            ("heading_1", "children"),
            ("heading_2", "children"),
            ("heading_3", "children"),
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
            return "|"

    def _finalize_open_parents(self, context: LineProcessingContext) -> None:
        """Finalize all open parent blocks - no toggle logic needed here anymore."""
        while context.parent_stack:
            parent_context = context.parent_stack.pop()

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
            ("column_list", "children"),
            ("column", "children"),
            ("heading_1", "children"),
            ("heading_2", "children"),
            ("heading_3", "children"),
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
