from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class UserType(StrEnum):
    PERSON = "person"
    BOT = "bot"


class WorkspaceOwnerType(StrEnum):
    USER = "user"
    WORKSPACE = "workspace"


class BotOwnerDto(BaseModel):
    type: WorkspaceOwnerType
    workspace: bool | None = None


class WorkspaceLimits(BaseModel):
    max_file_upload_size_in_bytes: int


class BotUserDto(BaseModel):
    owner: BotOwnerDto | None = None
    workspace_name: str | None = None
    workspace_limits: WorkspaceLimits | None = None


class _UserBase(BaseModel):
    id: str
    type: UserType
    name: str | None = None
    avatar_url: str | None = None


class PersonUserResponseDto(_UserBase):
    type: Literal[UserType.PERSON] = UserType.PERSON
    email: str | None = None


class BotUserResponseDto(_UserBase):
    type: Literal[UserType.BOT] = UserType.BOT
    bot: BotUserDto


UserResponseDto = Annotated[
    PersonUserResponseDto | BotUserResponseDto, Field(discriminator="type")
]


class UsersListResponseDto(BaseModel):
    results: list[UserResponseDto]
    next_cursor: str | None = None
    has_more: bool
