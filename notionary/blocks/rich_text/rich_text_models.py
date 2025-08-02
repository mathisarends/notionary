from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class TextAnnotations(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


class TextContent(BaseModel):
    content: str
    link: Optional[str] = None


class RichTextObject(BaseModel):
    type: str = "text"
    text: TextContent
    annotations: TextAnnotations
    plain_text: str
    href: Optional[str] = None

    @classmethod
    def from_plain_text(cls, content: str, **kwargs) -> RichTextObject:
        """Create rich text object from plain text with optional formatting."""
        annotations = TextAnnotations(**kwargs)
        text_content = TextContent(content=content, link=None)

        return cls(
            text=text_content, annotations=annotations, plain_text=content, href=None
        )
