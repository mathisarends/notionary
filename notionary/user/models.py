from dataclasses import dataclass

from notionary.user.schemas import WorkspaceOwnerType


@dataclass
class PersonUser:
    id: str
    name: str
    avatar_url: str
    email: str


@dataclass
class BotUser:
    id: str
    workspace_file_upload_limit_in_bytes: int
    owner_type: WorkspaceOwnerType
    name: str | None = None
    avatar_url: str | None = None
    workspace_name: str | None = None
