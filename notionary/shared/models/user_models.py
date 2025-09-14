from __future__ import annotations
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class ObjectType(StrEnum):
    """Notion object types."""

    USER = "user"


class UserType(StrEnum):
    """User type enumeration."""

    PERSON = "person"
    BOT = "bot"


class OwnerType(StrEnum):
    """Bot owner type enumeration."""

    WORKSPACE = "workspace"
    USER = "user"


class PersonObject(BaseModel):
    """Person object for User objects with type 'person'."""

    email: str | None = None


class BotOwner(BaseModel):
    """Bot owner information."""

    type: OwnerType
    workspace: bool | None = None


class WorkspaceLimits(BaseModel):
    """Workspace limits for bot users."""

    max_file_upload_size_in_bytes: int | None = None


class BotObject(BaseModel):
    """Bot object for User objects with type 'bot'."""

    owner: BotOwner | None = None
    workspace_name: str | None = None
    workspace_limits: WorkspaceLimits | None = None


class NotionUser(BaseModel):
    """
    Represents a User object in the Notion API.
    Users include full workspace members, guests, and integrations.
    """

    object: Literal["user"]
    id: str
    type: UserType | None = None
    name: str | None = None
    avatar_url: str | None = None

    person: PersonObject | None = None
    bot: BotObject | None = None
