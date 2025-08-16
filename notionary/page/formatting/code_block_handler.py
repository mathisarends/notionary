import re
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.code.code_element import CodeElement
from notionary.page.formatting.line_handler import (
    LineHandler,
    LineProcessingContext,
    ParentBlockContext,
)


class CodeBlockHandler(LineHandler):
    """Handles code block specific logic with batching."""

    def __init__(self):
        super().__init__()
        self._code_start_pattern = re.compile(r"^```(\w*)\s*$")
        self._code_end_pattern = re.compile(r"^```\s*$")
        self._caption_pattern = re.compile(r"^(?:Caption|caption):\s*(.+)$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_code_start(context) or self._is_caption_after_code_block(
            context
        )

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_code_start(context):
            self._process_complete_code_block(context)
            context.was_processed = True
            context.should_continue = True
            return

        if self._is_caption_after_code_block(context):
            self._add_caption_to_last_code_block(context)
            context.was_processed = True
            context.should_continue = True

    def _is_code_start(self, context: LineProcessingContext) -> bool:
        """Check if this line starts a code block."""
        return self._code_start_pattern.match(context.line.strip()) is not None

    def _process_complete_code_block(self, context: LineProcessingContext) -> None:
        """Process the entire code block in one go."""
        # Extract language from opening fence
        match = self._code_start_pattern.match(context.line.strip())
        language = match.group(1) if match and match.group(1) else ""

        # Create code block
        code_element = CodeElement()
        result = code_element.markdown_to_notion(context.line)
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
            block.code.rich_text = [RichTextObject.for_code_block(code_content)]

        # Tell the main loop to skip the consumed lines
        context.lines_consumed = lines_to_consume
        context.result_blocks.append(block)

    def _is_caption_after_code_block(self, context: LineProcessingContext) -> bool:
        """Check if this line is a caption for the last code block."""
        if not self._caption_pattern.match(context.line.strip()):
            return False

        if context.parent_stack:
            return False

        return self._last_block_is_code_block(context)

    def _last_block_is_code_block(self, context: LineProcessingContext) -> bool:
        """Check if the last block in result_blocks is a code block."""
        if not context.result_blocks:
            return False

        last_block = context.result_blocks[-1]
        return (hasattr(last_block, "type") and last_block.type == "code") or (
            hasattr(last_block, "code")
        )

    def _add_caption_to_last_code_block(self, context: LineProcessingContext) -> None:
        """Add caption to the last code block in result_blocks."""
        caption_text = self._extract_caption_text(context.line)
        if not caption_text:
            return

        if not context.result_blocks:
            return

        last_block = context.result_blocks[-1]

        if hasattr(last_block, "code"):
            caption_rich_text = RichTextObject.for_code_block(caption_text)
            last_block.code.caption.append(caption_rich_text)

    def _extract_caption_text(self, line: str) -> str:
        """Extract caption text from the line."""
        match = self._caption_pattern.match(line.strip())
        return match.group(1).strip() if match else ""
