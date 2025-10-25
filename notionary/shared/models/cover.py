from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel

from notionary.shared.models.file import ExternalFile


class CoverType(StrEnum):
    EXTERNAL = "external"
    FILE_UPLOAD = "file_upload"


class ExternalCover(BaseModel):
    type: Literal[CoverType.EXTERNAL] = CoverType.EXTERNAL
    external: ExternalFile

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(external=ExternalFile(url=url))


class FileUploadCover(BaseModel):
    type: Literal[CoverType.FILE_UPLOAD] = CoverType.FILE_UPLOAD
    id: str


Cover = ExternalCover | FileUploadCover
