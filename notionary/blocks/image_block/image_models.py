from typing import Literal, Optional

from pydantic import BaseModel, Field

from notionary.blocks.file.file_element_models import (
    ExternalFile,
    FileUploadFile,
    NotionHostedFile,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class ImageBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: list[RichTextObject] = Field(default_factory=list)


class CreateImageBlock(BaseModel):
    type: Literal["image"] = "image"
    image: ImageBlock
