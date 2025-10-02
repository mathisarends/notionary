from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.rich_text.models import RichText


class FileType(StrEnum):
    EXTERNAL = "external"
    FILE = "file"
    FILE_UPLOAD = "file_upload"


class ExternalFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str


class NotionHostedFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    expiry_time: str


class FileUploadFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str


class FileBlock(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    caption: list[RichText] = Field(default_factory=list)
    type: FileType
    external: ExternalFile | None = None
    file: NotionHostedFile | None = None
    file_upload: FileUploadFile | None = None
    name: str | None = None


class CreateFileBlock(BaseModel):
    type: Literal["file"] = "file"
    file: FileBlock
