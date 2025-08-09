from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import Block, BlockType
from notionary.blocks.todo.todo_models import CreateToDoBlock, ToDoBlock
from notionary.prompts import ElementPromptBuilder, ElementPromptContent
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class TodoElement(NotionBlockElement):
    """
    Handles conversion between Markdown todo items and Notion to_do blocks.

    Markdown syntax examples:
    - [ ] Unchecked todo item
    - [x] Checked todo item
    * [ ] Also works with asterisk
    + [ ] Also works with plus sign
    """

    PATTERN = re.compile(r"^\s*[-*+]\s+\[ \]\s+(.+)$")
    DONE_PATTERN = re.compile(r"^\s*[-*+]\s+\[x\]\s+(.+)$", re.IGNORECASE)

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text) or cls.DONE_PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.TO_DO and block.to_do

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown todo or done item to Notion to_do block."""
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
        rich = TextInlineFormatter.parse_inline_formatting(content)

        todo_content = ToDoBlock(
            rich_text=rich,
            checked=checked,
            color="default",
        )
        return CreateToDoBlock(to_do=todo_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion to_do block to markdown todo item."""
        if block.type != BlockType.TO_DO or not block.to_do:
            return None

        td = block.to_do
        content = TextInlineFormatter.extract_text_with_formatting(td.rich_text)
        checkbox = "[x]" if td.checked else "[ ]"
        return f"- {checkbox} {content}"

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates interactive to-do items with checkboxes that can be marked complete."
            )
            .with_usage_guidelines(
                "Use to-do items for task lists, checklists, or tracking progress on items."
            )
            .with_syntax("- [ ] Task to complete")
            .with_examples(
                [
                    "- [ ] Draft project proposal",
                    "- [x] Create initial timeline",
                    "* [ ] Review code changes",
                    "+ [x] Finalize handoff checklist",
                ]
            )
            .build()
        )
