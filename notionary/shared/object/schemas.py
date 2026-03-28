from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# File
# ---------------------------------------------------------------------------


class FileType(StrEnum):
    EXTERNAL = "external"
    FILE = "file"
    FILE_UPLOAD = "file_upload"


class ExternalFileData(BaseModel):
    url: str


class ExternalFile(BaseModel):
    type: Literal[FileType.EXTERNAL] = FileType.EXTERNAL
    external: ExternalFileData

    def get_url(self) -> str:
        return self.external.url

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(external=ExternalFileData(url=url))


class NotionHostedFileData(BaseModel):
    url: str
    expiry_time: str


class NotionHostedFile(BaseModel):
    type: Literal[FileType.FILE] = FileType.FILE
    file: NotionHostedFileData

    def get_url(self) -> str:
        return self.file.url


class FileUploadedFileData(BaseModel):
    id: UUID


class FileUploadFile(BaseModel):
    type: Literal[FileType.FILE_UPLOAD] = FileType.FILE_UPLOAD
    file_upload: FileUploadedFileData

    def get_url(self) -> None:
        return None


File = Annotated[
    ExternalFile | NotionHostedFile | FileUploadFile, Field(discriminator="type")
]


# ---------------------------------------------------------------------------
# Parent
# ---------------------------------------------------------------------------


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
