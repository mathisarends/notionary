from __future__ import annotations
from pydantic import BaseModel
from notionary.blocks.mappings.markdown_node import MarkdownNode


class NumberedListMarkdownBlockParams(BaseModel):
    text: str
    number: int = 1


class NumberedListMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown numbered list items.
    Example: 1. First step
    """

    def __init__(self, text: str, number: int = 1):
        self.text = text
        self.number = number

    @classmethod
    def from_params(
        cls, params: NumberedListMarkdownBlockParams
    ) -> NumberedListMarkdownBlock:
        return cls(text=params.text, number=params.number)

    def to_markdown(self) -> str:
        return f"{self.number}. {self.text}"
