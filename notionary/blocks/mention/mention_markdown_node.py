from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class MentionMarkdownBlockParams(BaseModel):
    mention_type: Literal["page", "database", "date"]
    value: str


class MentionMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown mentions.
    Supports: page, database, date.
    Examples: @[page-id], @db[database-id], @date[YYYY-MM-DD]
    """

    def __init__(self, mention_type: str, value: str):
        allowed = {"page", "database", "date"}
        if mention_type not in allowed:
            raise ValueError(f"mention_type must be one of {allowed}")
        self.mention_type = mention_type
        self.value = value

    @classmethod
    def from_params(cls, params: MentionMarkdownBlockParams) -> MentionMarkdownNode:
        return cls(mention_type=params.mention_type, value=params.value)

    def to_markdown(self) -> str:
        if self.mention_type == "page":
            return f"@[{self.value}]"
        elif self.mention_type == "database":
            return f"@db[{self.value}]"
        elif self.mention_type == "date":
            return f"@date[{self.value}]"
        else:
            return f"@[{self.value}]"
