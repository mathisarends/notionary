from typing import Literal

from pydantic import BaseModel

from notionary.blocks.file.file_element_models import FileBlock


class CreatePdfBlock(BaseModel):
    type: Literal["pdf"] = "pdf"
    pdf: FileBlock
