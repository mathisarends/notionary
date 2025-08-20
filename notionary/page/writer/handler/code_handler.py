import re

from notionary.blocks.code.code_element import CodeElement
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.writer.handler import LineHandler, LineProcessingContext


class CodeHandler(LineHandler):
    """Handles code block specific logic with batching.

    Markdown syntax:
    ```language "optional caption"
    code lines...
    ```
    """

    def __init__(self):
        super().__init__()
        self._code_start_pattern = re.compile(r"^```(\w*)\s*(?:\"([^\"]*)\")?\s*$")
        self._code_end_pattern = re.compile(r"^```\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        if self._is_inside_parent_context(context):
            return False
        return self._is_code_start(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_code_start(context):
            self._process_complete_code_block(context)
            self._mark_processed(context)

    def _is_code_start(self, context: LineProcessingContext) -> bool:
        """Check if this line starts a code block."""
        return self._code_start_pattern.match(context.line.strip()) is not None

    def _is_inside_parent_context(self, context: LineProcessingContext) -> bool:
        """Check if we're currently inside any parent context (toggle, heading, etc.)."""
        return len(context.parent_stack) > 0

    def _process_complete_code_block(self, context: LineProcessingContext) -> None:
        """Process the entire code block in one go."""
        # Extract language and caption from opening fence
        language, caption = self._extract_fence_info(context.line)

        # Create base code block
        result = CodeElement.markdown_to_notion(f"```{language}")
        if not result:
            return

        block = result[0] if isinstance(result, list) else result

        code_lines, lines_to_consume = self._collect_code_lines(context)

        self._set_block_content(block, code_lines)

        self._set_block_caption(block, caption)

        context.lines_consumed = lines_to_consume
        context.result_blocks.append(block)

    def _extract_fence_info(self, line: str) -> tuple[str, str]:
        """Extract the language and optional caption from a code fence."""
        match = self._code_start_pattern.match(line.strip())
        lang = match.group(1) if match and match.group(1) else ""
        cap = match.group(2) if match and match.group(2) else ""
        return lang, cap

    def _collect_code_lines(
        self, context: LineProcessingContext
    ) -> tuple[list[str], int]:
        """Collect lines until closing fence and return (lines, count_to_consume)."""
        lines = []
        for idx, ln in enumerate(context.get_remaining_lines()):
            if self._code_end_pattern.match(ln.strip()):
                return lines, idx + 1
            lines.append(ln)
        # No closing fence: consume all remaining
        rem = context.get_remaining_lines()
        return rem, len(rem)

    def _mark_processed(self, context: LineProcessingContext) -> None:
        """Mark context as processed and continue."""
        context.was_processed = True
        context.should_continue = True

    def _set_block_content(self, block, code_lines: list[str]) -> None:
        """Set the code rich_text content on the block."""
        if not code_lines:
            return
        content = "\n".join(code_lines)
        block.code.rich_text = [RichTextObject.for_code_block(content)]

    def _set_block_caption(self, block, caption: str) -> None:
        """Append caption to the code block if provided."""
        if not caption:
            return
        block.code.caption.append(RichTextObject.for_code_block(caption))
