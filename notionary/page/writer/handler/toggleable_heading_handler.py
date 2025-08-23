from __future__ import annotations

import re

from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.toggleable_heading.toggleable_heading_element import (
    ToggleableHeadingElement,
)
from notionary.blocks.types import BlockType
from notionary.page.writer.handler import (
    LineHandler,
    LineProcessingContext,
    ParentBlockContext,
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

    async def _process(self, context: LineProcessingContext) -> None:
        """Process toggleable heading start, end, or content with unified handling."""

        async def _handle(action):
            await action(context)
            context.was_processed = True
            context.should_continue = True
            return True

        if self._is_toggleable_heading_start(context):
            return await _handle(self._start_toggleable_heading)
        if self._is_toggleable_heading_end(context):
            return await _handle(self._finalize_toggleable_heading)
        if self._is_toggleable_heading_content(context):
            return await _handle(self._add_toggleable_heading_content)

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

    async def _start_toggleable_heading(self, context: LineProcessingContext) -> None:
        """Start a new toggleable heading block."""
        toggleable_heading_element = ToggleableHeadingElement()

        # Create the block
        result = await toggleable_heading_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result

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

    async def _add_toggleable_heading_content(self, context: LineProcessingContext) -> None:
        """Add content to the current toggleable heading context."""
        context.parent_stack[-1].add_child_line(context.line)

    async def _finalize_toggleable_heading(self, context: LineProcessingContext) -> None:
        """Finalize a toggleable heading block and add it to result_blocks."""
        heading_context = context.parent_stack.pop()

        if heading_context.has_children():
            all_children = await self._get_all_children(
                heading_context, context.block_registry
            )
            self._assign_heading_children(heading_context.block, all_children)

        # Check if we have a parent context to add this heading to
        if context.parent_stack:
            # Add this heading as a child block to the parent
            parent_context = context.parent_stack[-1]
            if hasattr(parent_context, "add_child_block"):
                parent_context.add_child_block(heading_context.block)
            else:
                # Fallback: add to result_blocks for backward compatibility
                context.result_blocks.append(heading_context.block)
        else:
            # No parent, add to top level
            context.result_blocks.append(heading_context.block)

    async def _get_all_children(
        self, parent_context: ParentBlockContext, block_registry
    ) -> list:
        """Helper method to combine text-based and direct block children."""
        children_blocks = []

        # Process text lines
        if parent_context.child_lines:
            children_text = "\n".join(parent_context.child_lines)
            text_blocks = await self._convert_children_text(children_text, block_registry)
            children_blocks.extend(text_blocks)

        # Add direct blocks
        if hasattr(parent_context, "child_blocks") and parent_context.child_blocks:
            children_blocks.extend(parent_context.child_blocks)

        return children_blocks

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

    async def _convert_children_text(self, text: str, block_registry) -> list:
        """Convert children text to blocks."""
        from notionary.page.writer.markdown_to_notion_converter import (
            MarkdownToNotionConverter,
        )

        if not text.strip():
            return []

        child_converter = MarkdownToNotionConverter(block_registry)
        return await child_converter.process_lines(text)
