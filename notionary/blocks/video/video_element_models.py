from typing import Literal, Optional

from pydantic import BaseModel, Field

from notionary.blocks.block_models import (
    ExternalFile,
    FileUploadFile,
    NotionHostedFile,
    RichTextObject,
)


class VideoBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: list[RichTextObject] = Field(default_factory=list)


class CreateVideoBlock(BaseModel):
    type: Literal["video"] = "video"
    video: VideoBlock
