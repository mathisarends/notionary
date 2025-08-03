from __future__ import annotations
import re

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.formatting.line_handler import LineHandler, LineProcessingContext


class CodeBlockHandler(LineHandler):
    """Handles code block specific logic including captions."""

    def __init__(self):
        super().__init__()
        self._code_end_pattern = re.compile(r"^```\s*$")
        self._caption_pattern = re.compile(r"^(?:Caption|caption):\s*(.+)$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return (
            self._is_code_end(context)
            or self._is_in_code_block(context)
            or self._is_caption_after_code_block(context)
        )

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_code_end(context):
            self._finalize_code_block(context)
            context.was_processed = True
            context.should_continue = True
            return

        if self._is_in_code_block(context):
            self._add_code_line(context)
            context.was_processed = True
            context.should_continue = True
            return

        if self._is_caption_after_code_block(context):
            self._add_caption_to_last_code_block(context)
            context.was_processed = True
            context.should_continue = True

    def _is_code_end(self, context: LineProcessingContext) -> bool:
        if not self._code_end_pattern.match(context.line.strip()):
            return False
        return (
            context.parent_stack
            and context.parent_stack[-1].element_type.__name__ == "CodeElement"
        )

    def _is_in_code_block(self, context: LineProcessingContext) -> bool:
        return (
            context.parent_stack
            and context.parent_stack[-1].element_type.__name__ == "CodeElement"
            and context.parent_stack[-1].child_prefix == "RAW"
        )

    def _is_caption_after_code_block(self, context: LineProcessingContext) -> bool:
        """Check if this line is a caption for the last code block."""
        # Must match caption pattern
        if not self._caption_pattern.match(context.line.strip()):
            return False

        # Must not be in an active code block
        if context.parent_stack:
            return False

        # Last block in result_blocks must be a code block
        return self._last_block_is_code_block(context)

    def _last_block_is_code_block(self, context: LineProcessingContext) -> bool:
        """Check if the last block in result_blocks is a code block."""
        if not context.result_blocks.blocks:
            return False

        last_block_info = context.result_blocks.blocks[-1]
        last_block = last_block_info.block

        return (hasattr(last_block, "type") and last_block.type == "code") or (
            hasattr(last_block, "code")
        )

    def _finalize_code_block(self, context: LineProcessingContext) -> None:
        """Finalize a code block."""
        code_context = context.parent_stack.pop()

        if code_context.has_children():
            code_content = "\n".join(code_context.child_lines)
            code_context.block.code.rich_text = [
                RichTextObject.for_code_block(code_content)
            ]

        context.result_blocks.add(
            code_context.start_position, context.current_pos, code_context.block
        )

    def _add_code_line(self, context: LineProcessingContext) -> None:
        """Add a line to the current code block."""
        context.parent_stack[-1].add_child_line(context.line)

    def _add_caption_to_last_code_block(self, context: LineProcessingContext) -> None:
        """Add caption to the last code block in result_blocks."""
        caption_text = self._extract_caption_text(context.line)
        if not caption_text:
            return

        if not context.result_blocks.blocks:
            return

        last_block_info = context.result_blocks.blocks[-1]
        last_block = last_block_info.block

        # Verify it's a code block and add caption
        if hasattr(last_block, "code"):
            # For CreateCodeBlock objects - add to caption list
            caption_rich_text = RichTextObject.from_plain_text(caption_text)
            last_block.code.caption.append(caption_rich_text)

    def _extract_caption_text(self, line: str) -> str:
        """Extract caption text from the line."""
        match = self._caption_pattern.match(line.strip())
        return match.group(1).strip() if match else ""
