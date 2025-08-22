from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from typing_extensions import Literal


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


class EquationObject(BaseModel):
    expression: str


class MentionUserRef(BaseModel):
    id: str  # Notion user id


class MentionPageRef(BaseModel):
    id: str


class MentionDatabaseRef(BaseModel):
    id: str


class MentionLinkPreview(BaseModel):
    url: str


class MentionDate(BaseModel):
    # entspricht Notion date object (start Pflicht, end/time_zone optional)
    start: str  # ISO 8601 date or datetime
    end: Optional[str] = None
    time_zone: Optional[str] = None


class MentionTemplateMention(BaseModel):
    # Notion hat zwei Template-Mention-Typen
    type: Literal["template_mention_user", "template_mention_date"]


class MentionObject(BaseModel):
    type: Literal[
        "user", "page", "database", "date", "link_preview", "template_mention"
    ]
    user: Optional[MentionUserRef] = None
    page: Optional[MentionPageRef] = None
    database: Optional[MentionDatabaseRef] = None
    date: Optional[MentionDate] = None
    link_preview: Optional[MentionLinkPreview] = None
    template_mention: Optional[MentionTemplateMention] = None


class RichTextObject(BaseModel):
    type: Literal["text", "mention", "equation"] = "text"

    text: Optional[TextContent] = None
    annotations: Optional[TextAnnotations] = None
    plain_text: str = ""
    href: Optional[str] = None

    mention: Optional[MentionObject] = None

    equation: Optional[EquationObject] = None

    @classmethod
    def from_plain_text(cls, content: str, **ann) -> RichTextObject:
        return cls(
            type="text",
            text=TextContent(content=content),
            annotations=TextAnnotations(**ann) if ann else TextAnnotations(),
            plain_text=content,
        )
        
    @classmethod
    def for_caption(cls, content: str) -> RichTextObject:
        return cls(
            type="text",
            text=TextContent(content=content),
            annotations=None,
            plain_text=content,
        )    

    # TODO: remove this when mixin is cpmplete
    @classmethod
    def for_code_block(cls, content: str) -> RichTextObject:
        # keine annotations setzen → Notion Code-Highlight bleibt an
        return cls.for_caption(content)

    @classmethod
    def for_link(cls, content: str, url: str, **ann) -> RichTextObject:
        return cls(
            type="text",
            text=TextContent(content=content, link=LinkObject(url=url)),
            annotations=TextAnnotations(**ann) if ann else TextAnnotations(),
            plain_text=content,
        )

    @classmethod
    def mention_user(cls, user_id: str) -> RichTextObject:
        return cls(
            type="mention",
            mention=MentionObject(type="user", user=MentionUserRef(id=user_id)),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_page(cls, page_id: str) -> RichTextObject:
        return cls(
            type="mention",
            mention=MentionObject(type="page", page=MentionPageRef(id=page_id)),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_database(cls, database_id: str) -> RichTextObject:
        return cls(
            type="mention",
            mention=MentionObject(
                type="database", database=MentionDatabaseRef(id=database_id)
            ),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_link_preview(cls, url: str) -> RichTextObject:
        return cls(
            type="mention",
            mention=MentionObject(
                type="link_preview", link_preview=MentionLinkPreview(url=url)
            ),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_date(
        cls, start: str, end: str | None = None, time_zone: str | None = None
    ) -> RichTextObject:
        return cls(
            type="mention",
            mention=MentionObject(
                type="date", date=MentionDate(start=start, end=end, time_zone=time_zone)
            ),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_template_user(cls) -> RichTextObject:
        return cls(
            type="mention",
            mention=MentionObject(
                type="template_mention",
                template_mention=MentionTemplateMention(type="template_mention_user"),
            ),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_template_date(cls) -> RichTextObject:
        return cls(
            type="mention",
            mention=MentionObject(
                type="template_mention",
                template_mention=MentionTemplateMention(type="template_mention_date"),
            ),
            annotations=TextAnnotations(),
        )

    @classmethod
    def equation_inline(cls, expression: str) -> RichTextObject:
        return cls(
            type="equation",
            equation=EquationObject(expression=expression),
            annotations=TextAnnotations(),
            plain_text=expression,  # Notion liefert plain_text serverseitig; für Roundtrip hilfreich
        )
