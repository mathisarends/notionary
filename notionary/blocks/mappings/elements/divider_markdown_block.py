from __future__ import annotations

from pydantic import BaseModel
from notionary.blocks.mappings.markdown_node import MarkdownNode


class DividerMarkdownBlockParams(BaseModel):
    pass


class DividerMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown divider lines (---).
    """

    def __init__(self):
        pass  # Keine Attribute notwendig

    @classmethod
    def from_params(cls, params: DividerMarkdownBlockParams) -> DividerMarkdownBlock:
        return cls()

    def to_markdown(self) -> str:
        return "---"
