import re
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.code.code_element import CodeElement
from notionary.page.formatting.line_handler import (
    LineHandler,
    LineProcessingContext,
)

class CodeBlockHandler(LineHandler):
    """Handles code block specific logic with batching."""

    def __init__(self):
        super().__init__()
        # Updated pattern to capture language and optional caption in quotes
        self._code_start_pattern = re.compile(r"^```(\w*)\s*(?:\"([^\"]*)\")?\s*$")
        self._code_end_pattern = re.compile(r"^```\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        # Don't handle code blocks if we're inside a toggle - let toggle handler collect the lines
        if self._is_inside_toggle(context):
            return False
        return self._is_code_start(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_code_start(context):
            self._process_complete_code_block(context)
            context.was_processed = True
            context.should_continue = True

    def _is_code_start(self, context: LineProcessingContext) -> bool:
        """Check if this line starts a code block."""
        return self._code_start_pattern.match(context.line.strip()) is not None

    def _is_inside_toggle(self, context: LineProcessingContext) -> bool:
        """Check if we're currently inside a toggle context."""
        if not context.parent_stack:
            return False
        
        from notionary.blocks.toggle.toggle_element import ToggleElement
        current_parent = context.parent_stack[-1]
        return issubclass(current_parent.element_type, ToggleElement)

    def _process_complete_code_block(self, context: LineProcessingContext) -> None:
        """Process the entire code block in one go."""
        # Extract language and caption from opening fence
        match = self._code_start_pattern.match(context.line.strip())
        language = match.group(1) if match and match.group(1) else ""
        caption = match.group(2) if match and match.group(2) else ""

        # Create code block with just the language part for CodeElement
        code_start_line = f"```{language}"
        code_element = CodeElement()
        result = code_element.markdown_to_notion(code_start_line)
        if not result:
            return

        block = result if not isinstance(result, list) else result[0]

        # Find all lines until closing fence
        code_lines = []
        remaining_lines = context.get_remaining_lines()
        lines_to_consume = 0

        for i, line in enumerate(remaining_lines):
            if self._code_end_pattern.match(line.strip()):
                lines_to_consume = i + 1  # Include the closing fence
                break
            code_lines.append(line)
        else:
            # No closing fence found - consume all remaining lines
            lines_to_consume = len(remaining_lines)
            code_lines = remaining_lines

        # Set the code content
        if code_lines:
            code_content = "\n".join(code_lines)
            if hasattr(block, 'code') and hasattr(block.code, 'rich_text'):
                block.code.rich_text = [RichTextObject.for_code_block(code_content)]

        # Set the caption if provided
        if caption and hasattr(block, 'code') and hasattr(block.code, 'caption'):
            caption_rich_text = RichTextObject.for_code_block(caption)
            block.code.caption.append(caption_rich_text)

        # Tell the main loop to skip the consumed lines
        context.lines_consumed = lines_to_consume
        context.result_blocks.append(block)