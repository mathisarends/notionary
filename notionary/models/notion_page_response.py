from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any, Union

from pydantic import BaseModel


@dataclass
class User:
    """Represents a Notion user object."""

    object: str
    id: str


@dataclass
class ExternalFile:
    """Represents an external file, e.g., for cover images."""

    url: str


@dataclass
class Cover:
    """Cover image for a Notion page."""

    type: str
    external: ExternalFile


@dataclass
class EmojiIcon:
    type: Literal["emoji"]
    emoji: str


@dataclass
class ExternalIcon:
    type: Literal["external"]
    external: ExternalFile


@dataclass
class FileObject:
    url: str
    expiry_time: str


@dataclass
class FileIcon:
    type: Literal["file"]
    file: FileObject


Icon = Union[EmojiIcon, ExternalIcon, FileIcon]


@dataclass
class DatabaseParent:
    type: Literal["database_id"]
    database_id: str


@dataclass
class PageParent:
    type: Literal["page_id"]
    page_id: str


@dataclass
class WorkspaceParent:
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
