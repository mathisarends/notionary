from pydantic import BaseModel
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Literal, Union

# Reusing existing types from your codebase
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
    type: Literal["page_id", "workspace", "block_id", "database_id"]
    page_id: Optional[str] = None
    block_id: Optional[str] = None
    database_id: Optional[str] = None

# Icon (reusing from your existing Icon import)
class NotionIcon(BaseModel):
    type: str  # 'emoji', 'external', 'file'
    emoji: Optional[str] = None

# Rich text types for Pydantic models
class TextContentPydantic(BaseModel):
    content: str
    link: Optional[Dict[str, str]] = None

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
    option_ids: List[str]

class StatusPropertySchema(BaseModel):
    options: List[StatusOption]
    groups: List[StatusGroup]

class DatabaseStatusProperty(BaseModel):
    id: str
    name: str
    type: Literal["status"]
    status: StatusPropertySchema

class RelationPropertySchema(BaseModel):
    database_id: str
    type: str  # "single_property"
    single_property: Dict[str, Any]

class DatabaseRelationProperty(BaseModel):
    id: str
    name: str
    type: Literal["relation"]
    relation: RelationPropertySchema

class DatabaseUrlProperty(BaseModel):
    id: str
    name: str
    type: Literal["url"]
    url: Dict[str, Any]  # Usually empty dict

class DatabaseRichTextProperty(BaseModel):
    id: str
    name: str
    type: Literal["rich_text"]
    rich_text: Dict[str, Any]  # Usually empty dict

class MultiSelectOption(BaseModel):
    id: str
    name: str
    color: str
    description: Optional[str] = None

class MultiSelectPropertySchema(BaseModel):
    options: List[MultiSelectOption]

class DatabaseMultiSelectProperty(BaseModel):
    id: str
    name: str
    type: Literal["multi_select"]
    multi_select: MultiSelectPropertySchema

class DatabaseTitleProperty(BaseModel):
    id: str
    name: str
    type: Literal["title"]
    title: Dict[str, Any]  # Usually empty dict

# Generic database property for unknown types
class GenericDatabaseProperty(BaseModel):
    id: str
    name: str
    type: str
    class Config:
        extra = "allow"

# Union of all database property types
DatabaseProperty = Union[
    DatabaseStatusProperty,
    DatabaseRelationProperty,
    DatabaseUrlProperty,
    DatabaseRichTextProperty,
    DatabaseMultiSelectProperty,
    DatabaseTitleProperty,
    GenericDatabaseProperty
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
    relation: List[RelationItem]
    has_more: bool

class UrlProperty(BaseModel):
    id: str
    type: str  # 'url'
    url: Optional[str] = None

class RichTextProperty(BaseModel):
    id: str
    type: str  # 'rich_text'
    rich_text: List[RichTextItemPydantic]

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
    title: List[RichTextItemPydantic]

# Cover types
class ExternalCover(BaseModel):
    url: str

class NotionCover(BaseModel):
    type: str  # 'external', 'file'
    external: Optional[ExternalCover] = None

# Parent types for Pydantic
class NotionParent(BaseModel):
    type: str  # 'database_id', 'page_id', 'workspace'
    database_id: Optional[str] = None
    page_id: Optional[str] = None

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
    cover: Optional[Any] = None
    icon: Optional[NotionIcon] = None
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    title: List[RichTextItemPydantic]
    description: List[Any]
    is_inline: bool
    properties: Dict[str, Any]  # Using Any for flexibility with different property schemas
    parent: NotionParent
    url: str
    public_url: Optional[str] = None
    archived: bool
    in_trash: bool

# Page object
@dataclass
class NotionPage(BaseModel):
    object: Literal["page"]
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

class NotionQueryResponse(BaseModel):
    """
    Complete Notion search/query response model that can contain both pages and databases.
    """
    object: Literal["list"]
    results: List[Union[NotionPage, NotionDatabaseResponse]]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: Dict[str, Any]
    request_id: str

# Specific response type for database queries (pages only)
class NotionQueryDatabaseResponse(BaseModel):
    """
    Notion database query response model for querying pages within a database.
    """
    object: Literal["list"]
    results: List[NotionPage]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: Dict[str, Any]
    request_id: str

# Specific response type for search results (can be mixed)
class NotionSearchResponse(BaseModel):
    """
    Notion search response model that can return both pages and databases.
    """
    object: Literal["list"]
    results: List[Union[NotionPage, NotionDatabaseResponse]]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: Dict[str, Any]
    request_id: str
    
class NotionDatabaseSearchResponse(BaseModel):
    """
    Notion search response model for database-only searches.
    """
    object: Literal["list"]
    results: List[NotionDatabaseResponse]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: Dict[str, Any]
    request_id: str