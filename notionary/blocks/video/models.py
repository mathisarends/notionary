from typing import Literal

from pydantic import BaseModel

from notionary.blocks.file.models import FileBlock


class CreateVideoBlock(BaseModel):
    type: Literal["video"] = "video"
    video: FileBlock
