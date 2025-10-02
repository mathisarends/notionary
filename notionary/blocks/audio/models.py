from typing import Literal

from pydantic import BaseModel

from notionary.blocks.file.models import FileBlock
from notionary.blocks.types import BlockType


class CreateAudioBlock(BaseModel):
    type: Literal[BlockType.AUDIO] = BlockType.AUDIO
    audio: FileBlock
