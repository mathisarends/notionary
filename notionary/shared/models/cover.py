from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel

from notionary.shared.models.file import ExternalFile


class CoverType(StrEnum):
    EXTERNAL = "external"
    FILE = "file"


class NotionCover(BaseModel):
    type: Literal[CoverType.EXTERNAL, CoverType.FILE] = CoverType.EXTERNAL
    external: ExternalFile | None = None

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(external=ExternalFile(url=url))
