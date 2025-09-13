from __future__ import annotations
from typing import Literal
from enum import StrEnum

from pydantic import BaseModel
from notionary.shared.models.file_models import ExternalFile, ExternalRessource


class CoverType(StrEnum):
    EXTERNAL = "external"
    FILE = "file"


class NotionCover(BaseModel):
    type: Literal[CoverType.EXTERNAL, CoverType.FILE] = CoverType.EXTERNAL
    external: ExternalFile | None = None


class UpdateCoverDto(BaseModel):
    cover: ExternalRessource | None = None

    @classmethod
    def from_url(cls, url: str) -> UpdateCoverDto:
        return cls(icon=ExternalRessource.from_url(url))
