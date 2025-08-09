from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class TextAnnotations(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


class LinkObject(BaseModel):
    url: str


class TextContent(BaseModel):
    content: str
    link: Optional[LinkObject] = None


class RichTextObject(BaseModel):
    type: str = "text"
    text: TextContent
    annotations: Optional[TextAnnotations] = None
    plain_text: str
    href: Optional[str] = None

    @classmethod
    def from_plain_text(cls, content: str, **kwargs) -> RichTextObject:
        annotations = TextAnnotations(**kwargs) if kwargs else None
        text_content = TextContent(content=content, link=None)
        return cls(
            text=text_content, annotations=annotations, plain_text=content, href=None
        )

    @classmethod
    def for_code_block(cls, content: str) -> RichTextObject:
        """
        Create a RichTextObject for code blocks.

        Note:
            Do not set any annotations here, as this will disable code highlighting in the Notion UI.
        """
        return cls(text=TextContent(content=content), plain_text=content, href=None)