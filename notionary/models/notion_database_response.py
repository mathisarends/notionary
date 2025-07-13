from pydantic import BaseModel
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Literal, Union

from notionary.models.notion_page_response import Icon


@dataclass
class TextContent:
    content: str
    link: Optional[str] = None


@dataclass
class RichText:
    type: str
    text: TextContent
    plain_text: str
    href: Optional[str]


@dataclass
class User:
    object: str
    id: str


@dataclass
class Parent:
    type: Literal["page_id", "workspace", "block_id"]
    page_id: Optional[str] = None
    block_id: Optional[str] = None  # Added block_id field


class NotionDatabaseResponse(BaseModel):
    """
    Represents the response from the Notion API when retrieving a database.
    """

    object: Literal["database"]
    id: str
    cover: Optional[Any]
    icon: Optional[Icon]
    created_time: str
    last_edited_time: str
    created_by: User
    last_edited_by: User
    title: List[RichText]
    description: List[Any]
    is_inline: bool
    properties: Dict[str, Any]
    parent: Parent
    url: str
    public_url: Optional[str]
    archived: bool
    in_trash: bool
    request_id: Optional[str] = None
    
    
# Basic types
class NotionUser(BaseModel):
    object: str  # 'user'
    id: str

# Cover types
class ExternalCover(BaseModel):
    url: str

class NotionCover(BaseModel):
    type: str  # 'external', 'file'
    external: Optional[ExternalCover] = None

# Icon types  
class NotionIcon(BaseModel):
    type: str  # 'emoji', 'external', 'file'
    emoji: Optional[str] = None

# Parent types
class NotionParent(BaseModel):
    type: str  # 'database_id', 'page_id', 'workspace'
    database_id: Optional[str] = None
    page_id: Optional[str] = None

# Rich text types
class TextContent(BaseModel):
    content: str
    link: Optional[Dict[str, str]] = None

class Annotations(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str

class RichTextItem(BaseModel):
    type: str  # 'text', 'mention', 'equation'
    text: Optional[TextContent] = None
    annotations: Annotations
    plain_text: str
    href: Optional[str] = None

# Property types
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
    relation: List[RelationItem]
    has_more: bool

class UrlProperty(BaseModel):
    id: str
    type: str  # 'url'
    url: Optional[str] = None

class RichTextProperty(BaseModel):
    id: str
    type: str  # 'rich_text'
    rich_text: List[RichTextItem]

class MultiSelectItem(BaseModel):
    id: str
    name: str
    color: str

class MultiSelectProperty(BaseModel):
    id: str
    type: str  # 'multi_select'
    multi_select: List[MultiSelectItem]

class TitleProperty(BaseModel):
    id: str
    type: str  # 'title'
    title: List[RichTextItem]

# Generic property for unknown types
class GenericProperty(BaseModel):
    id: str
    type: str
    # Allow any additional fields
    class Config:
        extra = "allow"

# Union of all property types
NotionProperty = Union[
    StatusProperty,
    RelationProperty, 
    UrlProperty,
    RichTextProperty,
    MultiSelectProperty,
    TitleProperty,
    GenericProperty
]

# Main page object
@dataclass
class NotionPage(BaseModel):
    object: str  # 'page'
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    cover: Optional[NotionCover] = None
    icon: Optional[NotionIcon] = None
    parent: NotionParent
    archived: bool
    in_trash: bool
    properties: Dict[str, Any]  # Using Any for flexibility with different property types
    url: str
    public_url: Optional[str] = None

# Query response
@dataclass
class NotionQueryDatabaseResponse(BaseModel):
    """
    Complete Notion database query response model based on actual API data.
    """
    object: str  # 'list'
    results: List[NotionPage]
    next_cursor: Optional[str] = None
    has_more: bool
    type: str  # 'page_or_database'
    page_or_database: Dict[str, Any]  # Usually empty dict
    request_id: str