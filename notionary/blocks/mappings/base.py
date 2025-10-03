from abc import ABC, abstractmethod
from typing import ClassVar

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, BlockCreatePayload
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class NotionMarkdownMapper(ABC):
    block_type: ClassVar[BlockType | None] = None

    @classmethod
    @abstractmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreatePayload:
        pass

    @classmethod
    @abstractmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        """Convert Notion block to markdown."""
        pass

    # Überlegen ob ich to_notion hier überhaupt brauche
    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        # Default implementation - subclasses should override this method
        # Cannot call async notion_to_markdown here
        return False

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for this block element.

        Subclasses should override this method to provide their specific information.
        Return None if the element should not be included in documentation.
        """
        return None
