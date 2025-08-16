from __future__ import annotations

from typing import Optional
from notionary.blocks.code.code_models import CodeBlock
from notionary.markdown.markdown_node import MarkdownNode


class CodeMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown code blocks.
    Example:
        ```python "Basic usage"
        print("Hello, world!")
        ```
    """

    def __init__(
        self,
        code: str,
        language: Optional[str] = None,
        caption: Optional[str] = None,
    ):
        self.code = code
        self.language = language or ""
        self.caption = caption

    @classmethod
    def from_params(cls, params: CodeBlock) -> CodeMarkdownNode:
        return cls(
            code=params.rich_text, language=params.language, caption=params.caption
        )

    def to_markdown(self) -> str:
        lang = self.language or ""

        # Build the opening fence with optional caption
        opening_fence = f"```{lang}"
        if self.caption:
            opening_fence += f' "{self.caption}"'

        content = f"{opening_fence}\n{self.code}\n```"
        return content
