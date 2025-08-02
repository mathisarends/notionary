from typing import Literal, Optional
from pydantic import BaseModel, Field

from notionary.blocks.block_models import (
    FileUploadFile,
    NotionHostedFile,
    RichTextObject,
)
from notionary.models.notion_page_response import ExternalFile


class AudioBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: list[RichTextObject] = Field(default_factory=list)


class CreateAudioBlock(BaseModel):
    type: Literal["audio"] = "audio"
    audio: AudioBlock
