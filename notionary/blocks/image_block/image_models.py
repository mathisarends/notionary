from typing import Literal

from pydantic import BaseModel

from notionary.blocks.file.file_element_models import (
    FileBlock,
)


class CreateImageBlock(BaseModel):
    type: Literal["image"] = "image"
    image: FileBlock
