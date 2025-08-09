from typing import Literal, Optional
from enum import Enum

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from typing import Literal


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
    caption: list[RichTextObject] = Field(default_factory=list)
    type: FileType
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    name: Optional[str] = None


class CreateFileBlock(BaseModel):
    type: Literal["file"] = "file"
    file: FileBlock
