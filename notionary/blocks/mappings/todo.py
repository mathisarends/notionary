import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockColor, BlockType, CreateToDoBlock, ToDoData
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class TodoMapper(NotionMarkdownMapper):
    """
    Markdown syntax examples:
    - [ ] Unchecked todo item
    - [x] Checked todo item
    * [ ] Also works with asterisk
    + [ ] Also works with plus sign
    """

    PATTERN = re.compile(r"^\s*[-*+]\s+\[ \]\s+(.+)$")
    DONE_PATTERN = re.compile(r"^\s*[-*+]\s+\[x\]\s+(.+)$", re.IGNORECASE)

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.TO_DO and block.to_do

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateToDoBlock:
        m_done = cls.DONE_PATTERN.match(text)
        m_todo = None if m_done else cls.PATTERN.match(text)

        if m_done:
            content = m_done.group(1)
            checked = True
        elif m_todo:
            content = m_todo.group(1)
            checked = False
        else:
            return None

        # build rich text
        converter = MarkdownRichTextConverter()
        rich = await converter.to_rich_text(content)

        todo_content = ToDoData(
            rich_text=rich,
            checked=checked,
            color=BlockColor.DEFAULT,
        )
        return CreateToDoBlock(to_do=todo_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        """Convert Notion to_do block to markdown todo item."""
        if block.type != BlockType.TO_DO or not block.to_do:
            return None

        td = block.to_do
        converter = RichTextToMarkdownConverter()
        content = await converter.to_markdown(td.rich_text)
        checkbox = "[x]" if td.checked else "[ ]"
        return f"- {checkbox} {content}"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for todo blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Todo blocks create interactive checkboxes for task management",
            syntax_examples=[
                "- [ ] Unchecked todo item",
                "- [x] Checked todo item",
                "* [ ] Todo with asterisk",
                "+ [ ] Todo with plus sign",
                "- [x] Completed task",
            ],
            usage_guidelines="Use for task lists and checkboxes. [ ] for unchecked, [x] for checked items. Supports -, *, or + as bullet markers. Interactive in Notion interface.",
        )
