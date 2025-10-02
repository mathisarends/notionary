from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichText


class FileType(str, Enum):
    EXTERNAL = "external"
    FILE = "file"
    FILE_UPLOAD = "file_upload"


class ExternalFile(BaseModel):
    url: str


class NotionHostedFile(BaseModel):
    url: str
    expiry_time: str


class FileUploadFile(BaseModel):
    id: str


class FileBlock(BaseModel):
    caption: list[RichText] = Field(default_factory=list)
    type: FileType
    external: ExternalFile | None = None
    file: NotionHostedFile | None = None
    file_upload: FileUploadFile | None = None
    name: str | None = None


class CreateFileBlock(BaseModel):
    type: Literal["file"] = "file"
    file: FileBlock
