from __future__ import annotations
import re

from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.block_types import BlockType
from notionary.blocks.toggleable_heading.toggleable_heading_element import (
    ToggleableHeadingElement,
)
from notionary.page.writer.context import ParentBlockContext
from notionary.page.writer.line_handler import (
    LineHandler,
    LineProcessingContext,
)


class ToggleableHeadingHandler(LineHandler):
    """Handles toggleable heading blocks with +++# syntax."""

    def __init__(self):
        super().__init__()
        self._start_pattern = re.compile(
            r"^[+]{3}(?P<level>#{1,3})\s+(.+)$", re.IGNORECASE
        )
        # +++
        self._end_pattern = re.compile(r"^[+]{3}\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return (
            self._is_toggleable_heading_start(context)
            or self._is_toggleable_heading_end(context)
            or self._is_toggleable_heading_content(context)
        )

    def _process(self, context: LineProcessingContext) -> None:
        """Process toggleable heading start, end, or content with unified handling."""

        def _handle(action):
            action(context)
            context.was_processed = True
            context.should_continue = True
            return True

        if self._is_toggleable_heading_start(context):
            return _handle(self._start_toggleable_heading)
        if self._is_toggleable_heading_end(context):
            return _handle(self._finalize_toggleable_heading)
        if self._is_toggleable_heading_content(context):
            return _handle(self._add_toggleable_heading_content)

    def _is_toggleable_heading_start(self, context: LineProcessingContext) -> bool:
        """Check if line starts a toggleable heading (+++# "Title")."""
        return self._start_pattern.match(context.line.strip()) is not None

    def _is_toggleable_heading_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a toggleable heading (+++)."""
        if not self._end_pattern.match(context.line.strip()):
            return False

        if not context.parent_stack:
            return False

        # Check if top of stack is a ToggleableHeading
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ToggleableHeadingElement)

    def _start_toggleable_heading(self, context: LineProcessingContext) -> None:
        """Start a new toggleable heading block."""
        toggleable_heading_element = ToggleableHeadingElement()

        # Create the block
        result = toggleable_heading_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result if not isinstance(result, list) else result[0]

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=ToggleableHeadingElement,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    def _is_toggleable_heading_content(self, context: LineProcessingContext) -> bool:
        """Check if we're inside a toggleable heading context and should handle content."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not issubclass(current_parent.element_type, ToggleableHeadingElement):
            return False

        # Handle all content inside toggleable heading (not start/end patterns)
        line = context.line.strip()
        return not (self._start_pattern.match(line) or self._end_pattern.match(line))

    def _add_toggleable_heading_content(self, context: LineProcessingContext) -> None:
        """Add content to the current toggleable heading context."""
        context.parent_stack[-1].add_child_line(context.line)

    def _finalize_toggleable_heading(self, context: LineProcessingContext) -> None:
        """Finalize a toggleable heading block and add it to result_blocks."""
        heading_context = context.parent_stack.pop()

        if heading_context.has_children():
            children_text = "\n".join(heading_context.child_lines)
            children_blocks = self._convert_children_text(
                children_text, context.block_registry
            )
            self._assign_heading_children(heading_context.block, children_blocks)

        context.result_blocks.append(heading_context.block)

    def _assign_heading_children(
        self, parent_block: BlockCreateRequest, children: list[BlockCreateRequest]
    ) -> None:
        """Assign children to toggleable heading blocks."""
        block_type = parent_block.type

        if block_type == BlockType.HEADING_1:
            parent_block.heading_1.children = children
        elif block_type == BlockType.HEADING_2:
            parent_block.heading_2.children = children
        elif block_type == BlockType.HEADING_3:
            parent_block.heading_3.children = children

    def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.writer.markdown_to_notion_converter import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return child_converter._process_lines(text)
