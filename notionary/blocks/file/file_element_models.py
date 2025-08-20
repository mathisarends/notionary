from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichTextObject


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
