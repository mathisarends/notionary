from typing import Literal
from enum import StrEnum

from pydantic import BaseModel


class ParentType(StrEnum):
    DATABASE_ID = "database_id"
    PAGE_ID = "page_id"
    WORKSPACE = "workspace"


class NotionParent(BaseModel):
    type: Literal[ParentType.DATABASE_ID, ParentType.PAGE_ID, ParentType.WORKSPACE]
    database_id: str | None = None
    page_id: str | None = None
