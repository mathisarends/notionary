from typing import Literal

from pydantic import BaseModel


class NotionUserDto(BaseModel):
    object: Literal["user"] = "user"
    id: str


class UserContextMixin(BaseModel):
    created_by: NotionUserDto
    last_edited_by: NotionUserDto
