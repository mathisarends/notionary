from pydantic import BaseModel
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Literal

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
