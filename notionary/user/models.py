from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel


class PersonUser(BaseModel):
    """Person user details"""

    email: str | None = None


class BotOwner(BaseModel):
    """Bot owner information - simplified structure"""

    type: Literal["workspace", "user"]
    workspace: bool | None = None


class WorkspaceLimits(BaseModel):
    """Workspace limits for bot users"""

    max_file_upload_size_in_bytes: int


class BotUser(BaseModel):
    """Bot user details"""

    owner: BotOwner | None = None
    workspace_name: str | None = None
    workspace_limits: WorkspaceLimits | None = None


class NotionUserResponse(BaseModel):
    """
    Represents a Notion user object as returned by the Users API.
    Can represent both person and bot users.
    """

    object: Literal["user"]
    id: str
    type: Literal["person", "bot"] | None = None
    name: str | None = None
    avatar_url: str | None = None

    # Person-specific fields
    person: PersonUser | None = None

    # Bot-specific fields
    bot: BotUser | None = None


class NotionBotUserResponse(NotionUserResponse):
    """
    Specialized response for bot user (from /users/me endpoint)
    """

    # Bot users should have these fields, but they can still be None
    type: Literal["bot"]
    bot: BotUser | None = None


class NotionUsersListResponse(BaseModel):
    """
    Response model for paginated users list from /v1/users endpoint.
    Follows Notion's standard pagination pattern.
    """

    object: Literal["list"]
    results: list[NotionUserResponse]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["user"]
    user: dict = {}


@dataclass
class WorkspaceInfo:
    """Dataclass to hold workspace information for bot users."""

    name: str | None = None
    limits: WorkspaceLimits | None = None
    owner_type: str | None = None
    is_workspace_owned: bool = False
