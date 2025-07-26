from __future__ import annotations
from pydantic import BaseModel
from notionary.blocks.mappings.markdown_node import MarkdownNode


class NumberedListMarkdownBlockParams(BaseModel):
    texts: list[str]


class NumberedListMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown numbered list items.
    Example:
    1. First step
    2. Second step
    3. Third step
    """

    def __init__(self, texts: list[str]):
        self.texts = texts

    @classmethod
    def from_params(
        cls, params: NumberedListMarkdownBlockParams
    ) -> NumberedListMarkdownBlock:
        return cls(texts=params.texts)

    def to_markdown(self) -> str:
        return "\n".join(f"{i + 1}. {text}" for i, text in enumerate(self.texts))
