from typing import Literal, Optional, Dict, Any, Union

from pydantic import BaseModel


class User(BaseModel):
    """Represents a Notion user object."""

    object: str
    id: str


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


class DatabaseParent(BaseModel):
    type: Literal["database_id"]
    database_id: str


class PageParent(BaseModel):
    type: Literal["page_id"]
    page_id: str


class WorkspaceParent(BaseModel):
    type: Literal["workspace"]
    workspace: bool = True


Parent = Union[DatabaseParent, PageParent, WorkspaceParent]


class NotionPageResponse(BaseModel):
    """
    Represents a full Notion page object as returned by the Notion API.

    This structure is flexible and designed to work with different database schemas.
    """

    object: str
    id: str
    created_time: str
    last_edited_time: str
    created_by: User
    last_edited_by: User
    cover: Optional[Cover]
    icon: Optional[Icon]
    parent: Parent
    archived: bool
    in_trash: bool
    properties: Dict[str, Any]
    url: str
    public_url: Optional[str]
    request_id: str
