from typing import Literal

from pydantic import BaseModel

from notionary.blocks.file.models import FileBlock
from notionary.blocks.types import BlockType


class CreateImageBlock(BaseModel):
    type: Literal[BlockType.IMAGE] = BlockType.IMAGE
    image: FileBlock
