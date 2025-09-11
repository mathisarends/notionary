from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict

from notionary.blocks.models import ParentObject


class TextContent(BaseModel):
    content: str
    link: Optional[str] = None


class RichText(BaseModel):
    type: str
    text: TextContent
    plain_text: str
    href: Optional[str] = None


class User(BaseModel):
    object: str
    id: str


class Parent(BaseModel):
    type: Literal["page_id", "workspace", "block_id", "database_id"]
    page_id: Optional[str] = None
    block_id: Optional[str] = None
    database_id: Optional[str] = None


# Rich text types for Pydantic models
class TextContentPydantic(BaseModel):
    content: str
    link: Optional[dict[str, str]] = None


class Annotations(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str


class RichTextItemPydantic(BaseModel):
    type: str  # 'text', 'mention', 'equation'
    text: Optional[TextContentPydantic] = None
    annotations: Annotations
    plain_text: str
    href: Optional[str] = None


# Cover and Icon types
class ExternalFile(BaseModel):
    """Represents an external file, e.g., for cover images."""

    url: str


class Cover(BaseModel):
    """Cover image for a Notion page."""

    type: str
    external: ExternalFile


class EmojiIcon(BaseModel):
    type: Literal["emoji"]
    emoji: str


class ExternalIcon(BaseModel):
    type: Literal["external"]
    external: ExternalFile


Icon = Union[EmojiIcon, ExternalIcon]


# Database property schema types (these are schema definitions, not values)
class StatusOption(BaseModel):
    id: str
    name: str
    color: str
    description: Optional[str] = None


class StatusGroup(BaseModel):
    id: str
    name: str
    color: str
    option_ids: list[str]


class StatusPropertySchema(BaseModel):
    options: list[StatusOption]
    groups: list[StatusGroup]


class DatabaseStatusProperty(BaseModel):
    id: str
    name: str
    type: Literal["status"]
    status: StatusPropertySchema


class RelationPropertySchema(BaseModel):
    database_id: str
    type: str  # "single_property"
    single_property: dict[str, Any]


class DatabaseRelationProperty(BaseModel):
    id: str
    name: str
    type: Literal["relation"]
    relation: RelationPropertySchema


class DatabaseUrlProperty(BaseModel):
    id: str
    name: str
    type: Literal["url"]
    url: dict[str, Any]  # Usually empty dict


class DatabaseRichTextProperty(BaseModel):
    id: str
    name: str
    type: Literal["rich_text"]
    rich_text: dict[str, Any]  # Usually empty dict


class MultiSelectOption(BaseModel):
    id: str
    name: str
    color: str
    description: Optional[str] = None


class MultiSelectPropertySchema(BaseModel):
    options: list[MultiSelectOption]


class DatabaseMultiSelectProperty(BaseModel):
    id: str
    name: str
    type: Literal["multi_select"]
    multi_select: MultiSelectPropertySchema


class DatabaseTitleProperty(BaseModel):
    id: str
    name: str
    type: Literal["title"]
    title: dict[str, Any]  # Usually empty dict


# Generic database property for unknown types
class GenericDatabaseProperty(BaseModel):
    id: str
    name: str
    type: str

    model_config = ConfigDict(extra="allow")


# Union of all database property types
DatabaseProperty = Union[
    DatabaseStatusProperty,
    DatabaseRelationProperty,
    DatabaseUrlProperty,
    DatabaseRichTextProperty,
    DatabaseMultiSelectProperty,
    DatabaseTitleProperty,
    GenericDatabaseProperty,
]


# Page property value types (these are actual values, not schemas)
class StatusValue(BaseModel):
    id: str
    name: str
    color: str


class StatusProperty(BaseModel):
    id: str
    type: str  # 'status'
    status: Optional[StatusValue] = None


class RelationItem(BaseModel):
    id: str


class RelationProperty(BaseModel):
    id: str
    type: str  # 'relation'
    relation: list[RelationItem]
    has_more: bool


class UrlProperty(BaseModel):
    id: str
    type: str  # 'url'
    url: Optional[str] = None


class RichTextProperty(BaseModel):
    id: str
    type: str  # 'rich_text'
    rich_text: list[RichTextItemPydantic]


class MultiSelectItem(BaseModel):
    id: str
    name: str
    color: str


class MultiSelectProperty(BaseModel):
    id: str
    type: str  # 'multi_select'
    multi_select: list[MultiSelectItem]


class TitleProperty(BaseModel):
    id: str
    type: str  # 'title'
    title: list[RichTextItemPydantic]


# Cover types
class ExternalCover(BaseModel):
    url: str


class NotionCover(BaseModel):
    type: str  # 'external', 'file'
    external: Optional[ExternalCover] = None

# User type for Pydantic
class NotionUser(BaseModel):
    object: str  # 'user'
    id: str


# Database object
class NotionDatabaseResponse(BaseModel):
    """
    Represents the response from the Notion API when retrieving a database.
    """

    object: Literal["database"]
    id: str
    cover: Optional[Cover] = None
    icon: Optional[Icon] = None
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    title: list[RichTextItemPydantic]
    description: list[Any]
    is_inline: bool
    properties: dict[
        str, Any
    ]  # Using Any for flexibility with different property schemas
    parent: ParentObject
    url: str
    public_url: Optional[str] = None
    archived: bool
    in_trash: bool


class NotionPageResponse(BaseModel):
    object: Literal["page"]
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    cover: Optional[NotionCover] = None
    icon: Optional[Icon] = None
    parent: ParentObject
    archived: bool
    in_trash: bool
    properties: dict[str, Any]
    url: str
    public_url: Optional[str] = None


# Specific response type for database queries (pages only)
class NotionQueryDatabaseResponse(BaseModel):
    """
    Notion database query response model for querying pages within a database.
    """

    object: Literal["list"]
    results: list[NotionPageResponse]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str


class NotionDatabaseSearchResponse(BaseModel):
    """
    Notion search response model for database-only searches.
    """

    object: Literal["list"]
    results: list[NotionDatabaseResponse]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str
