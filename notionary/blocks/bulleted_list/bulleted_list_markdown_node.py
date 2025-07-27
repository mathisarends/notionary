from __future__ import annotations

from pydantic import BaseModel
from typing import List
from notionary.blocks.toggle.markdown_node import MarkdownNode


class BulletedListMarkdownBlockParams(BaseModel):
    texts: List[str]


class BulletedListMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown bulleted list items.
    Example:
    - First item
    - Second item
    - Third item
    """

    def __init__(self, texts: List[str]):
        self.texts = texts

    @classmethod
    def from_params(
        cls, params: BulletedListMarkdownBlockParams
    ) -> BulletedListMarkdownNode:
        return cls(texts=params.texts)

    def to_markdown(self) -> str:
        result = []
        for text in self.texts:
            result.append(f"- {text}")
        return "\n".join(result)
