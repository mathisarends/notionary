from __future__ import annotations

from pydantic import BaseModel
from notionary.blocks.toggle.markdown_node import MarkdownNode


class DividerMarkdownBlockParams(BaseModel):
    pass


class DividerMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown divider lines (---).
    """

    def __init__(self):
        pass  # Keine Attribute notwendig

    @classmethod
    def from_params(cls, params: DividerMarkdownBlockParams) -> DividerMarkdownNode:
        return cls()

    def to_markdown(self) -> str:
        return "---"
