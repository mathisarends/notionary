from typing import Literal, Optional

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichTextObject


class ExternalFile(BaseModel):
    url: str


class NotionHostedFile(BaseModel):
    url: str
    expiry_time: str


class FileUploadFile(BaseModel):
    id: str


class FileObject(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: Optional[list[RichTextObject]] = None
    name: Optional[str] = None


class FileBlock(BaseModel):
    caption: list[RichTextObject] = Field(default_factory=list)
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    name: Optional[str] = None


class CreateFileBlock(BaseModel):
    type: Literal["file"] = "file"
    file: FileBlock
