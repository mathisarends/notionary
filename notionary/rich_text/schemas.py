from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator, Field, Tag


class RichTextType(StrEnum):
    TEXT = "text"
    EQUATION = "equation"
    MENTION = "mention"


class MentionType(StrEnum):
    USER = "user"
    PAGE = "page"
    DATABASE = "database"
    DATE = "date"
    LINK_PREVIEW = "link_preview"


class LinkObject(BaseModel):
    url: str


class TextContent(BaseModel):
    content: str
    link: LinkObject | None = None


class EquationObject(BaseModel):
    expression: str


class TextAnnotations(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


class MentionPageRef(BaseModel):
    id: str


class MentionUserRef(BaseModel):
    id: str


class MentionDatabaseRef(BaseModel):
    id: str


class MentionDate(BaseModel):
    start: str
    end: str | None = None
    time_zone: str | None = None


class PageMention(BaseModel):
    type: Literal[MentionType.PAGE] = MentionType.PAGE
    page: MentionPageRef


class UserMention(BaseModel):
    type: Literal[MentionType.USER] = MentionType.USER
    user: MentionUserRef


class DatabaseMention(BaseModel):
    type: Literal[MentionType.DATABASE] = MentionType.DATABASE
    database: MentionDatabaseRef


class DateMention(BaseModel):
    type: Literal[MentionType.DATE] = MentionType.DATE
    date: MentionDate


class LinkPreviewMention(BaseModel):
    type: Literal[MentionType.LINK_PREVIEW] = MentionType.LINK_PREVIEW
    link_preview: LinkObject


AnyMention = Annotated[
    Annotated[PageMention, Tag("page")]
    | Annotated[UserMention, Tag("user")]
    | Annotated[DatabaseMention, Tag("database")]
    | Annotated[DateMention, Tag("date")]
    | Annotated[LinkPreviewMention, Tag("link_preview")],
    Discriminator("type"),
]


class RichText(BaseModel):
    type: RichTextType = RichTextType.TEXT
    plain_text: str = ""
    text: TextContent | None = None
    equation: EquationObject | None = None
    mention: AnyMention | None = None
    annotations: TextAnnotations = Field(default_factory=TextAnnotations)
    href: str | None = None

    @classmethod
    def from_plain_text(cls, content: str) -> "RichText":
        return cls(
            type=RichTextType.TEXT,
            plain_text=content,
            text=TextContent(content=content),
        )
