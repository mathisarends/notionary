from __future__ import annotations

from typing import Any
from pydantic import BaseModel
from enum import Enum

from notionary.blocks.block_models import Block


class ParseActionType(Enum):
    """Types of actions that can be taken during parsing"""

    START_CONTAINER = "start_container"
    END_CONTAINER = "end_container"
    ADD_CHILD_CONTENT = "add_child_content"
    ADD_SIBLING_BLOCK = "add_sibling_block"
    IGNORE = "ignore"


class ParseAction:
    """Represents an action to take during markdown parsing"""

    def __init__(self, action_type: ParseActionType, **kwargs):
        self.type = action_type
        self.block = kwargs.get("block")
        self.content = kwargs.get("content")
        self.data = kwargs

    @classmethod
    def start_container(cls, block: Any) -> ParseAction:
        return cls(ParseActionType.START_CONTAINER, block=block)

    @classmethod
    def end_container(cls) -> ParseAction:
        return cls(ParseActionType.END_CONTAINER)

    @classmethod
    def add_child_content(cls, content: str) -> ParseAction:
        return cls(ParseActionType.ADD_CHILD_CONTENT, content=content)

    @classmethod
    def add_sibling_block(cls, block: Any) -> ParseAction:
        return cls(ParseActionType.ADD_SIBLING_BLOCK, block=block)

    @classmethod
    def ignore(cls) -> ParseAction:
        return cls(ParseActionType.IGNORE)


class BlockParsingCapabilities(BaseModel):
    """Defines how a block element behaves during parsing"""

    priority: int = 1  # Higher = parsed first
    can_have_children: bool = False
    requires_context_stack: bool = False
    multiline: bool = False
    content_markers: list[str] = []  # Generic markers like ["+++", "|"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BlockContext:
    """Represents the parsing context for a block"""

    def __init__(self, block: Block, element_class: Any):
        self.block = block
        self.element_class = element_class
        self.children: list[Block] = []
        self.content_lines: list[str] = []

    def add_child(self, child: Block):
        """Add a child block"""
        self.children.append(child)

    def add_content(self, content: str):
        """Add content line"""
        self.content_lines.append(content)

    def finalize(self) -> Block:
        """Finalize the block with its children/content"""
        if not (hasattr(self.block, "children") and self.children):
            return self.block

        if hasattr(self.block, "children"):
            self.block.children = self.children
            return self.block

        return self.block


class RootBlockContext(BlockContext):
    """Special context for the root level"""

    def __init__(self):
        super().__init__(block=None, element_class=None)

    def finalize(self) -> list[Any]:
        """Return all children as the final result"""
        return self.children
