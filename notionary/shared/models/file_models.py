from __future__ import annotations
from typing import Literal
from enum import StrEnum
from pydantic import BaseModel


class FileType(StrEnum):
    EXTERNAL = "external"


class ExternalFile(BaseModel):
    """Represents an external file, e.g., for cover images."""

    url: str


class ExternalRessource(BaseModel):
    type: Literal[FileType.EXTERNAL] = FileType.EXTERNAL
    external: ExternalFile

    @classmethod
    def from_url(cls, url: str) -> ExternalRessource:
        return cls(external=ExternalFile(url=url))
