from typing import Literal
from pydantic import BaseModel

from notionary.blocks.file.file_element_models import FileBlock


class CreateAudioBlock(BaseModel):
    type: Literal["audio"] = "audio"
    audio: FileBlock
