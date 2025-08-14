from typing import Literal

from pydantic import BaseModel

from notionary.blocks.file.file_element_models import FileBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class CreatePdfBlock(BaseModel):
    type: Literal["pdf"] = "pdf"
    pdf: FileBlock
