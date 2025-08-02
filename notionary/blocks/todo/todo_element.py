import re
from typing import Any, Optional

from notionary.blocks import NotionBlockElement
from notionary.blocks import ElementPromptContent, ElementPromptBuilder
from notionary.blocks.shared.models import Block, ToDoBlock
from notionary.blocks.shared.text_inline_formatter import TextInlineFormatter


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
        return block.type == "to_do" and block.to_do is not None

    @classmethod
    def markdown_to_notion(cls, text: str) -> ToDoBlock | None:
        """Convert markdown todo or done item to a Notion ToDoBlock, or None if no match."""
        # Determine if it's done or todo
        m_done = cls.DONE_PATTERN.match(text.strip())
        m_todo = None if m_done else cls.PATTERN.match(text.strip())

        if m_done:
            content = m_done.group(1)
            checked = True
        elif m_todo:
            content = m_todo.group(1)
            checked = False
        else:
            return None

        rich = TextInlineFormatter.parse_inline_formatting(content)

        return ToDoBlock(rich_text=rich, checked=checked, color="default")

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion to_do block to markdown todo item."""
        if block.type != "to_do" or block.to_do is None:
            return None
        td = block.to_do
        checked = td.checked
        # extract formatted content
        rich_list = td.rich_text
        content = TextInlineFormatter.extract_text_with_formatting(
            [rt.model_dump() for rt in rich_list]
        )
        checkbox = "[x]" if checked else "[ ]"
        return f"- {checkbox} {content}"

    @classmethod
    def is_multiline(cls) -> bool:
        return False

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
