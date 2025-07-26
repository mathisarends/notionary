from typing import Optional
from notionary.blocks.mappings.markdown_node import MarkdownNode


class CodeMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Notion-style Markdown code blocks.
    Example:
        ```python
        print("Hello, world!")
        ```
        Caption: Basic usage
    """

    def __init__(
        self, code: str, language: Optional[str] = None, caption: Optional[str] = None
    ):
        self.code = code
        self.language = language or ""
        self.caption = caption

    def to_markdown(self) -> str:
        lang = self.language or ""
        # Always add a newline after the language; then the code (ends without \n if code already has line breaks)
        content = f"```{lang}\n{self.code}\n```"
        if self.caption:
            content += f"\nCaption: {self.caption}"
        return content
