from __future__ import annotations

import re

from notionary.blocks.toggle.toggle_element import ToggleElement
from notionary.page.writer.handler import (LineHandler, LineProcessingContext,
                                           ParentBlockContext)


class ToggleHandler(LineHandler):
    """Handles regular toggle blocks with ultra-simplified +++ syntax."""

    def __init__(self):
        super().__init__()
        self._start_pattern = re.compile(r"^[+]{3}\s+(.+)$", re.IGNORECASE)
        self._end_pattern = re.compile(r"^[+]{3}\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return (
            self._is_toggle_start(context)
            or self._is_toggle_end(context)
            or self._is_toggle_content(context)
        )

    def _process(self, context: LineProcessingContext) -> None:
        # Explicit, readable branches (small duplication is acceptable)
        if self._is_toggle_start(context):
            self._start_toggle(context)
            context.was_processed = True
            context.should_continue = True

        if self._is_toggle_end(context):
            self._finalize_toggle(context)
            context.was_processed = True
            context.should_continue = True

        if self._is_toggle_content(context):
            self._add_toggle_content(context)
            context.was_processed = True
            context.should_continue = True

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

        block = result

        # Push to parent stack
        parent_context = ParentBlockContext(
            block=block,
            element_type=ToggleElement,
            child_lines=[],
        )
        context.parent_stack.append(parent_context)

    def _finalize_toggle(self, context: LineProcessingContext) -> None:
        """Finalize a toggle block and add it to result_blocks."""
        toggle_context = context.parent_stack.pop()

        if toggle_context.has_children():
            all_children = self._get_all_children(
                toggle_context, context.block_registry
            )
            toggle_context.block.toggle.children = all_children

        # Check if we have a parent context to add this toggle to
        if context.parent_stack:
            # Add this toggle as a child block to the parent
            parent_context = context.parent_stack[-1]
            parent_context.add_child_block(toggle_context.block)
        else:
            # No parent, add to top level
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
        from notionary.page.writer.markdown_to_notion_converter import \
            MarkdownToNotionConverter

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return child_converter._process_lines(text)

    def _get_all_children(self, parent_context, block_registry) -> list:
        """Helper method to combine text-based and direct block children."""
        children_blocks = []

        # Process text lines
        if parent_context.child_lines:
            children_text = "\n".join(parent_context.child_lines)
            text_blocks = self._convert_children_text(children_text, block_registry)
            children_blocks.extend(text_blocks)

        # Add direct blocks (like processed columns)
        if hasattr(parent_context, "child_blocks") and parent_context.child_blocks:
            children_blocks.extend(parent_context.child_blocks)

        return children_blocks
