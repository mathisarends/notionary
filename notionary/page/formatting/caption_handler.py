import re

from notionary.page.formatting.line_handler import LineHandler, LineProcessingContext


class CaptionHandler(LineHandler):
    """Handles caption lines after code blocks."""

    def __init__(self):
        super().__init__()
        self._caption_pattern = re.compile(r"^(?:Caption|caption):\s*(.+)$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._caption_pattern.match(context.line.strip()) is not None

    def _process(self, context: LineProcessingContext) -> None:
        context.was_processed = True
        context.should_continue = True
