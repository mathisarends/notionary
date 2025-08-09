from __future__ import annotations

from pydantic import BaseModel
from notionary.markdown.markdown_node import MarkdownNode


class BreadcrumbMarkdownBlockParams(BaseModel):
    """Parameters for breadcrumb markdown block. No parameters needed."""

    pass


class BreadcrumbMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown breadcrumb blocks.
    Example:
    [breadcrumb]
    """

    def __init__(self):
        # No parameters needed for breadcrumb
        pass

    @classmethod
    def from_params(
        cls, params: BreadcrumbMarkdownBlockParams
    ) -> BreadcrumbMarkdownNode:
        return cls()

    def to_markdown(self) -> str:
        return "[breadcrumb]"
