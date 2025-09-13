from typing import Literal
from enum import StrEnum

from pydantic import BaseModel


# TODO: What about integrations here
class UserObjectType(StrEnum):
    USER = "user"


class NotionUser(BaseModel):
    object: Literal[UserObjectType.USER]
    id: str
