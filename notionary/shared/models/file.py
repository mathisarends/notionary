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
    id: str


class FileUploadFile(BaseModel):
    type: Literal[FileType.FILE_UPLOAD] = FileType.FILE_UPLOAD
    file_upload: FileUploadedFileData

    def get_url(self) -> None:
        return None


type File = Annotated[
    ExternalFile | NotionHostedFile | FileUploadFile, Field(discriminator="type")
]
