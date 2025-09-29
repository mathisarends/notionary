from enum import StrEnum

from pydantic import BaseModel


class UserType(StrEnum):
    PERSON = "person"
    BOT = "bot"


class WorkspaceOwnerType(StrEnum):
    USER = "user"
    WORKSPACE = "workspace"


class PersonUser(BaseModel):
    email: str | None = None


class BotOwner(BaseModel):
    type: WorkspaceOwnerType
    workspace: bool | None = None


class WorkspaceLimits(BaseModel):
    max_file_upload_size_in_bytes: int


class BotUser(BaseModel):
    owner: BotOwner | None = None
    workspace_name: str | None = None
    workspace_limits: WorkspaceLimits | None = None


class NotionPersonResponse(BaseModel):
    id: str
    type: UserType = UserType.PERSON
    name: str | None = None
    avatar_url: str | None = None
    person: PersonUser


class NotionBotResponse(BaseModel):
    id: str
    type: UserType = UserType.BOT
    name: str | None = None
    avatar_url: str | None = None
    bot: BotUser


NotionUserResponse = NotionPersonResponse | NotionBotResponse


class NotionUsersListResponse(BaseModel):
    results: list[NotionUserResponse]
    next_cursor: str | None = None
    has_more: bool
