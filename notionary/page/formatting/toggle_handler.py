from __future__ import annotations
import re

from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.block_types import BlockType
from notionary.blocks.toggle.toggle_element import ToggleElement
from notionary.page.formatting.line_handler import (
    LineHandler,
    LineProcessingContext,
    ParentBlockContext,
)


class ToggleHandler(LineHandler):
    """Handles regular toggle blocks with ultra-simplified +++ syntax."""

    def __init__(self):
        super().__init__()
        # ✅ FIXED: +++ Title (ultra-simplified - no "toggle", no quotes!)
        self._start_pattern = re.compile(r"^[+]{3}\s+(.+)$", re.IGNORECASE)
        # +++
        self._end_pattern = re.compile(r"^[+]{3}\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return (
            self._is_toggle_start(context)
            or self._is_toggle_end(context)
            or self._is_toggle_content(context)
        )

    def _process(self, context: LineProcessingContext) -> None:
        def _handle_and_continue(action_func):
            action_func(context)
            context.was_processed = True
            context.should_continue = True
            return True

        if self._is_toggle_start(context):
            return _handle_and_continue(self._start_toggle)

        if self._is_toggle_end(context):
            return _handle_and_continue(self._finalize_toggle)

        if self._is_toggle_content(context):
            return _handle_and_continue(self._add_toggle_content)

    def _is_toggle_start(self, context: LineProcessingContext) -> bool:
        """Check if line starts a toggle (+++ Title)."""
        line = context.line.strip()

        # Must match our pattern
        if not self._start_pattern.match(line):
            return False

        # But NOT match toggleable heading pattern (has # after +++)
        toggleable_heading_pattern = re.compile(r"^[+]{3}#{1,3}\s+.+$", re.IGNORECASE)
        if toggleable_heading_pattern.match(line):
            return False

        return True

    def _is_toggle_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a toggle (+++)."""
        if not self._end_pattern.match(context.line.strip()):
            return False

        if not context.parent_stack:
            return False

        # Check if top of stack is a Toggle
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ToggleElement)

    def _start_toggle(self, context: LineProcessingContext) -> None:
        """Start a new toggle block."""
        toggle_element = ToggleElement()

        # Create the block
        result = toggle_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result if not isinstance(result, list) else result[0]

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=ToggleElement,
            child_prefix="",  # No prefix needed
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    def _finalize_toggle(self, context: LineProcessingContext) -> None:
        """Finalize a toggle block and add it to result_blocks."""
        toggle_context = context.parent_stack.pop()

        if toggle_context.has_children():
            children_text = "\n".join(toggle_context.child_lines)
            children_blocks = self._convert_children_text(
                children_text, context.block_registry
            )
            toggle_context.block.toggle.children = children_blocks

        context.result_blocks.append(toggle_context.block)

    def _is_toggle_content(self, context: LineProcessingContext) -> bool:
        """Check if we're inside a toggle context and should handle content."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not issubclass(current_parent.element_type, ToggleElement):
            return False

        # Handle all content inside toggle (not start/end patterns)
        line = context.line.strip()
        return not (self._start_pattern.match(line) or self._end_pattern.match(line))

    def _add_toggle_content(self, context: LineProcessingContext) -> None:
        """Add content to the current toggle context."""
        context.parent_stack[-1].add_child_line(context.line)

    def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.formatting.markdown_to_notion_converter import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return child_converter._process_lines(text)
