import re
from typing import Optional
from notionary.blocks.block_models import Block
from notionary.blocks.column.column_models import ColumnListBlock, CreateColumnListBlock
from notionary.blocks.notion_block_element import BlockCreateResult, NotionBlockElement
from notionary.prompts import ElementPromptBuilder, ElementPromptContent


class ColumnElement(NotionBlockElement):
    """
    Simplified ColumnElement that works with the stack-based converter.
    Children (columns) are automatically handled by the StackBasedLineProcessor.
    """

    COLUMNS_START = re.compile(r"^:::\s*columns\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text starts a columns block."""
        return bool(cls.COLUMNS_START.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion column_list."""
        return block.type == "column_list"

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert markdown column start to Notion ColumnListBlock.
        Columns are automatically handled by the StackBasedLineProcessor.
        """
        if not cls.COLUMNS_START.match(text.strip()):
            return None

        # Return a ColumnListBlock with empty children - will be populated by stack processor
        column_list_content = ColumnListBlock()
        return CreateColumnListBlock(column_list=column_list_content)

    @classmethod
    def is_multiline(cls) -> bool:
        """Returns False because children are now handled automatically."""
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns structured LLM prompt metadata for the column layout element."""
        return (
            ElementPromptBuilder()
            .with_description(
                "Creates a multi-column layout that displays content side by side."
            )
            .with_usage_guidelines(
                "Use columns sparingly, only for direct comparisons or when parallel presentation significantly improves readability."
            )
            .with_syntax(
                "::: columns\n"
                "::: column\n"
                "Content for first column\n"
                ":::\n"
                "::: column\n"
                "Content for second column\n"
                ":::\n"
                ":::"
            )
            .with_examples(
                [
                    "::: columns\n"
                    "::: column\n"
                    "## Features\n"
                    "- Fast response time\n"
                    ":::\n"
                    "::: column\n"
                    "## Benefits\n"
                    "- Increased productivity\n"
                    ":::\n"
                    ":::"
                ]
            )
            .build()
        )
