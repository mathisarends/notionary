from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class UserType(StrEnum):
    PERSON = "person"
    BOT = "bot"


class WorkspaceOwnerType(StrEnum):
    USER = "user"
    WORKSPACE = "workspace"


class PersonUserDto(BaseModel):
    email: str | None = None


class BotOwnerDto(BaseModel):
    type: WorkspaceOwnerType
    workspace: bool | None = None


class WorkspaceLimits(BaseModel):
    max_file_upload_size_in_bytes: int


class BotUserDto(BaseModel):
    owner: BotOwnerDto | None = None
    workspace_name: str | None = None
    workspace_limits: WorkspaceLimits | None = None


class NotionUserBase(BaseModel):
    object: Literal["user"] = "user"
    id: str

    type: UserType

    name: str | None = None
    avatar_url: str | None = None


class PersonUserResponseDto(NotionUserBase):
    type: Literal[UserType.PERSON] = UserType.PERSON
    person: PersonUserDto


class BotUserResponseDto(NotionUserBase):
    type: Literal[UserType.BOT] = UserType.BOT
    bot: BotUserDto


UserResponseDto = Annotated[
    PersonUserResponseDto | BotUserResponseDto, Field(discriminator="type")
]


class NotionUsersListResponse(BaseModel):
    results: list[UserResponseDto]
    next_cursor: str | None = None
    has_more: bool


class PartialUserDto(BaseModel):
    object: Literal["user"] = "user"
    id: str
