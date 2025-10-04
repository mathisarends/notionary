import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.schemas import Block, BlockType, ColumnListData, CreateColumnListBlock


class ColumnListMapper(NotionMarkdownMapper):
    COLUMNS_START = re.compile(r"^:::\s*columns\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text starts a columns container."""
        return bool(cls.COLUMNS_START.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion column_list."""
        return block.type == BlockType.COLUMN_LIST and block.column_list

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateColumnListBlock:
        """Convert `::: columns` to Notion ColumnListBlock."""
        if not cls.COLUMNS_START.match(text.strip()):
            return None

        # Empty ColumnListData - children (columns) added by stack processor
        column_list_content = ColumnListData()
        return CreateColumnListBlock(column_list=column_list_content)
