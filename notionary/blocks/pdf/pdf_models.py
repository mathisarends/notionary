from typing import Literal

from pydantic import BaseModel

from notionary.blocks.file.file_element_models import FileBlock
from notionary.blocks.types import BlockType


class CreatePdfBlock(BaseModel):
    type: Literal[BlockType.PDF] = BlockType.PDF
    pdf: FileBlock
