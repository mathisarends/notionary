from __future__ import annotations

from pydantic import BaseModel
from notionary.blocks.mappings.markdown_node import MarkdownNode


class ParagraphMarkdownBlockParams(BaseModel):
    text: str


class ParagraphMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Markdown paragraphs.
    Paragraphs are standard text without special block formatting.
    """

    def __init__(self, text: str):
        self.text = text

    @classmethod
    def from_params(
        cls, params: ParagraphMarkdownBlockParams
    ) -> ParagraphMarkdownBlock:
        return cls(text=params.text)

    def to_markdown(self) -> str:
        return self.text
