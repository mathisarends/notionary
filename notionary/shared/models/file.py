from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field


class FileType(StrEnum):
    EXTERNAL = "external"
    FILE = "file"
    FILE_UPLOAD = "file_upload"


class ExternalFileData(BaseModel):
    url: str


class ExternalFile(BaseModel):
    type: Literal[FileType.EXTERNAL] = FileType.EXTERNAL
    external: ExternalFileData

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(external=ExternalFileData(url=url))


class NotionHostedFileData(BaseModel):
    url: str
    expiry_time: str


class NotionHostedFile(BaseModel):
    type: Literal[FileType.FILE] = FileType.FILE
    file: NotionHostedFileData


class FileUploadedFileData(BaseModel):
    id: str


class FileUploadFile(BaseModel):
    type: Literal[FileType.FILE_UPLOAD] = FileType.FILE_UPLOAD
    file_upload: FileUploadedFileData

    @classmethod
    def from_id(cls, id: str) -> Self:
        return cls(file_upload=FileUploadedFileData(id=id))


type File = Annotated[ExternalFile | NotionHostedFile | FileUploadFile, Field(discriminator="type")]
