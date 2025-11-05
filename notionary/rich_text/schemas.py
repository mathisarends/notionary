from enum import StrEnum
from typing import Self

from pydantic import BaseModel

from notionary.blocks.enums import BlockColor


class RichTextType(StrEnum):
    TEXT = "text"
    MENTION = "mention"
    EQUATION = "equation"


class MentionType(StrEnum):
    USER = "user"
    PAGE = "page"
    DATABASE = "database"
    DATASOURCE = "data_source"
    DATE = "date"
    LINK_PREVIEW = "link_preview"
    TEMPLATE_MENTION = "template_mention"


class TemplateMentionType(StrEnum):
    USER = "template_mention_user"
    DATE = "template_mention_date"


class TextAnnotations(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: BlockColor | None = None


class LinkObject(BaseModel):
    url: str


class TextContent(BaseModel):
    content: str
    link: LinkObject | None = None


class EquationObject(BaseModel):
    expression: str


class MentionUserRef(BaseModel):
    id: str  # Notion user id


class MentionPageRef(BaseModel):
    id: str


class MentionDatabaseRef(BaseModel):
    id: str


class MentionDataSourceRef(BaseModel):
    id: str


class MentionLinkPreview(BaseModel):
    url: str


class MentionDate(BaseModel):
    # entspricht Notion date object (start Pflicht, end/time_zone optional)
    start: str  # ISO 8601 date or datetime
    end: str | None = None
    time_zone: str | None = None


class MentionTemplateMention(BaseModel):
    # Notion hat zwei Template-Mention-Typen
    type: TemplateMentionType


class Mention(BaseModel):
    type: MentionType
    user: MentionUserRef | None = None
    page: MentionPageRef | None = None
    database: MentionDatabaseRef | None = None
    data_source: MentionDataSourceRef | None = None
    date: MentionDate | None = None
    link_preview: MentionLinkPreview | None = None
    template_mention: MentionTemplateMention | None = None


class RichText(BaseModel):
    type: RichTextType = RichTextType.TEXT

    text: TextContent | None = None
    annotations: TextAnnotations | None = None
    plain_text: str = ""
    href: str | None = None

    mention: Mention | None = None

    equation: EquationObject | None = None

    @classmethod
    def from_plain_text(cls, content: str, **ann) -> Self:
        return cls(
            type=RichTextType.TEXT,
            text=TextContent(content=content),
            annotations=TextAnnotations(**ann) if ann else TextAnnotations(),
            plain_text=content,
        )

    @classmethod
    def for_caption(cls, content: str) -> Self:
        return cls(
            type=RichTextType.TEXT,
            text=TextContent(content=content),
            annotations=None,
            plain_text=content,
        )

    @classmethod
    def for_code_block(cls, content: str) -> Self:
        return cls.for_caption(content)

    @classmethod
    def for_link(cls, content: str, url: str, **ann) -> Self:
        return cls(
            type=RichTextType.TEXT,
            text=TextContent(content=content, link=LinkObject(url=url)),
            annotations=TextAnnotations(**ann) if ann else TextAnnotations(),
            plain_text=content,
        )

    @classmethod
    def mention_user(cls, user_id: str) -> Self:
        return cls(
            type=RichTextType.MENTION,
            mention=Mention(type=MentionType.USER, user=MentionUserRef(id=user_id)),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_page(cls, page_id: str) -> Self:
        return cls(
            type=RichTextType.MENTION,
            mention=Mention(type=MentionType.PAGE, page=MentionPageRef(id=page_id)),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_database(cls, database_id: str) -> Self:
        return cls(
            type=RichTextType.MENTION,
            mention=Mention(
                type=MentionType.DATABASE, database=MentionDatabaseRef(id=database_id)
            ),
            annotations=TextAnnotations(),
        )

    @classmethod
    def mention_data_source(cls, data_source_id: str) -> Self:
        return cls(
            type=RichTextType.MENTION,
            mention=Mention(
                type=MentionType.DATASOURCE,
                data_source=MentionDataSourceRef(id=data_source_id),
            ),
            annotations=TextAnnotations(),
        )

    @classmethod
    def equation_inline(cls, expression: str) -> Self:
        return cls(
            type=RichTextType.EQUATION,
            equation=EquationObject(expression=expression),
            annotations=TextAnnotations(),
            plain_text=expression,
        )
