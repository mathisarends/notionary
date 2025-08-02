from typing import Literal, Optional
from pydantic import BaseModel, Field
from notionary.blocks.block_models import (
    ExternalFile,
    FileUploadFile,
    NotionHostedFile,
    RichTextObject,
)


class PdfBlock(BaseModel):
    caption: list[RichTextObject] = Field(default_factory=list)
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None


class CreatePdfBlock(BaseModel):
    type: Literal["pdf"] = "pdf"
    pdf: PdfBlock
