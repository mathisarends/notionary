from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel


class FileType(StrEnum):
    EXTERNAL = "external"


class ExternalFile(BaseModel):
    url: str


class ExternalRessource(BaseModel):
    type: Literal[FileType.EXTERNAL] = FileType.EXTERNAL
    external: ExternalFile

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(external=ExternalFile(url=url))
