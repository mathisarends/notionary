from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ParentType(StrEnum):
    DATABASE_ID = "database_id"
    DATA_SOURCE_ID = "data_source_id"
    PAGE_ID = "page_id"
    BLOCK_ID = "block_id"
    WORKSPACE = "workspace"


class DataSourceParent(BaseModel):
    type: Literal[ParentType.DATA_SOURCE_ID]
    data_source_id: UUID
    database_id: UUID


class PageParent(BaseModel):
    type: Literal[ParentType.PAGE_ID]
    page_id: UUID


class BlockParent(BaseModel):
    type: Literal[ParentType.BLOCK_ID]
    block_id: UUID


class WorkspaceParent(BaseModel):
    type: Literal[ParentType.WORKSPACE]
    workspace: bool


class DatabaseParent(BaseModel):
    type: Literal[ParentType.DATABASE_ID]
    database_id: UUID


type Parent = (
    DataSourceParent | PageParent | BlockParent | WorkspaceParent | DatabaseParent
)
