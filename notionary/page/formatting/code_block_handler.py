from __future__ import annotations
import re


from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.formatting.line_handler import LineHandler, LineProcessingContext


class CodeBlockHandler(LineHandler):
    """Handles code block specific logic."""

    def __init__(self):
        super().__init__()
        self._code_end_pattern = re.compile(r"^```\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_code_end(context) or self._is_in_code_block(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_code_end(context):
            self._finalize_code_block(context)
            context.was_processed = True
            context.should_continue = True
        elif self._is_in_code_block(context):
            self._add_code_line(context)
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

    def _finalize_code_block(self, context: LineProcessingContext) -> None:
        """Finalize a code block."""
        code_context = context.parent_stack.pop()

        if code_context.has_children():
            code_content = "\n".join(code_context.child_lines)
            code_context.block.code.rich_text = [RichTextObject.for_code_block(code_content)]

        context.result_blocks.add(
            code_context.start_position, context.current_pos, code_context.block
        )

    def _add_code_line(self, context: LineProcessingContext) -> None:
        """Add a line to the current code block."""
        context.parent_stack[-1].add_child_line(context.line)
