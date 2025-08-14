from __future__ import annotations
import re

from notionary.blocks.block_models import BlockCreateRequest
from notionary.blocks.block_types import BlockType
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.toggle.toggle_element import ToggleElement
from notionary.blocks.toggleable_heading.toggleable_heading_element import (
    ToggleableHeadingElement,
)
from notionary.page.formatting.line_handler import (
    LineHandler,
    LineProcessingContext,
    ParentBlockContext,
)


class ToggleHandler(LineHandler):
    """Handles toggle-specific logic for both regular toggles and toggleable headings."""

    def __init__(self):
        super().__init__()
        self._toggle_content_pattern = re.compile(r"^\|\s(.*)$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_toggle_end(context) or self._is_toggle_content(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_toggle_end(context):
            self._finalize_toggle(context)
            # Don't set was_processed=True, let the line be processed as a regular line
            return

        if self._is_toggle_content(context):
            self._add_toggle_content(context)
            context.was_processed = True
            context.should_continue = True

    def _is_toggle_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a toggle block."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not self._is_toggle_context(current_parent):
            return False

        # Toggle ends on:
        # 1. Empty line
        # 2. Line that doesn't start with | (new block at same level)
        line = context.line.strip()
        return not line or not line.startswith("|")  # Empty line  # Non-toggle content

    def _is_toggle_content(self, context: LineProcessingContext) -> bool:
        """Check if this is toggle content (| prefix) in an active toggle."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if not self._is_toggle_context(current_parent):
            return False

        # Check for | prefix
        return self._toggle_content_pattern.match(context.line) is not None

    def _is_toggle_context(self, parent_context: ParentBlockContext) -> bool:
        """Check if the parent context is a toggle or toggleable heading."""
        return (
            issubclass(
                parent_context.element_type, (ToggleElement, ToggleableHeadingElement)
            )
            and parent_context.child_prefix == "|"
        )

    def _finalize_toggle(self, context: LineProcessingContext) -> None:
        """Finalize a toggle block and add it to result_blocks."""
        toggle_context = context.parent_stack.pop()

        if toggle_context.has_children():
            children_text = "\n".join(toggle_context.child_lines)
            children_blocks = self._convert_children_text(
                children_text, context.block_registry
            )
            self._assign_toggle_children(toggle_context.block, children_blocks)

        context.result_blocks.append(toggle_context.block)

    def _add_toggle_content(self, context: LineProcessingContext) -> None:
        """Add content to the current toggle context."""
        match = self._toggle_content_pattern.match(context.line)
        if match:
            content = match.group(1)
            print("content", content)
            context.parent_stack[-1].add_child_line(content)

    def _convert_children_text(
        self, text: str, block_registry: BlockRegistry
    ) -> list[BlockCreateRequest]:
        """Convert children text to blocks."""
        from notionary.page.formatting.markdown_to_notion_converter import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        print("text", text)
        return child_converter._process_lines(text)

    def _assign_toggle_children(
        self, parent_block: BlockCreateRequest, children: list[BlockCreateRequest]
    ) -> None:
        """Assign children to toggle or toggleable heading blocks."""

        block_type = parent_block.type

        if block_type == BlockType.HEADING_1:
            parent_block.heading_1.children = children
        elif block_type == BlockType.HEADING_2:
            parent_block.heading_2.children = children
        elif block_type == BlockType.HEADING_3:
            parent_block.heading_3.children = children
        elif block_type == BlockType.TOGGLE:
            parent_block.toggle.children = children
