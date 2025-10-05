"""Parser for todo/checkbox blocks."""

import re
from typing import override

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockColor, CreateToDoBlock, ToDoData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)


class TodoParser(LineParser):
    """Handles todo/checkbox blocks with [ ] or [x] syntax."""

    PATTERN = re.compile(r"^\s*[-*+]\s+\[ \]\s+(.+)$")
    DONE_PATTERN = re.compile(r"^\s*[-*+]\s+\[x\]\s+(.+)$", re.IGNORECASE)

    def __init__(self, rich_text_converter: MarkdownRichTextConverter | None = None):
        super().__init__()
        self._rich_text_converter = rich_text_converter or MarkdownRichTextConverter()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False

        return self.PATTERN.match(context.line) is not None or self.DONE_PATTERN.match(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        block = await self._create_todo_block(context.line)
        if block:
            context.result_blocks.append(block)

    async def _create_todo_block(self, text: str) -> CreateToDoBlock | None:
        m_done = self.DONE_PATTERN.match(text)
        m_todo = None if m_done else self.PATTERN.match(text)

        if m_done:
            content = m_done.group(1)
            checked = True
        elif m_todo:
            content = m_todo.group(1)
            checked = False
        else:
            return None

        rich_text = await self._rich_text_converter.to_rich_text(content)
        todo_content = ToDoData(
            rich_text=rich_text,
            checked=checked,
            color=BlockColor.DEFAULT,
        )
        return CreateToDoBlock(to_do=todo_content)
