from dataclasses import dataclass
from uuid import UUID


@dataclass
class Person:
    """A human workspace member."""

    id: UUID
    name: str
    email: str
    avatar_url: str | None = None


@dataclass
class Bot:
    """A bot integration in the workspace."""

    id: UUID
    name: str | None
    workspace_name: str | None
    workspace_file_upload_limit_in_bytes: int
    avatar_url: str | None = None


type User = Person | Bot
