from enum import StrEnum
from pathlib import Path
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_serializer,
    model_validator,
)


class FileUploadConfig(BaseModel):
    _MB = 1024 * 1024

    _SINGLE_PART_MAX_SIZE: int = 20 * _MB
    _MAX_FILENAME_BYTES: int = 900
    _CHUNK_SIZE_MIN: int = 5 * _MB
    _CHUNK_SIZE_MAX: int = 20 * _MB
    _CHUNK_SIZE_DEFAULT: int = 10 * _MB

    model_config = ConfigDict(frozen=True)

    multi_part_chunk_size: int = Field(
        default=_CHUNK_SIZE_DEFAULT,
        ge=_CHUNK_SIZE_MIN,
        le=_CHUNK_SIZE_MAX,
        description="Part size (in bytes) for multi-part uploads. Notion allows 5MB–20MB.",
    )
    max_upload_timeout: int = Field(default=300, gt=0)
    poll_interval: int = Field(default=2, gt=0)
    base_upload_path: Path | None = Field(default=None)


class UploadMode(StrEnum):
    SINGLE_PART = "single_part"
    MULTI_PART = "multi_part"


class FileUploadStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"
    EXPIRED = "expired"


class FileUploadResponse(BaseModel):
    id: UUID
    created_time: str
    last_edited_time: str
    expiry_time: str | None = None
    upload_url: str | None = None
    in_trash: bool
    status: FileUploadStatus
    filename: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    request_id: UUID | None = None


class FileUploadFilter(BaseModel):
    status: FileUploadStatus | None = None
    in_trash: bool | None = None


class FileUploadListResponse(BaseModel):
    results: list[FileUploadResponse]
    next_cursor: str | None = None
    has_more: bool


class FileUploadCreateRequest(BaseModel):
    filename: str = Field(..., max_length=900)
    content_type: str | None = None
    content_length: int | None = None
    mode: UploadMode = UploadMode.SINGLE_PART
    number_of_parts: int | None = Field(None, ge=1)

    @model_validator(mode="after")
    def validate_multipart_requirements(self):
        if self.mode == UploadMode.MULTI_PART and self.number_of_parts is None:
            raise ValueError("number_of_parts is required when mode is 'multi_part'")
        if self.mode == UploadMode.SINGLE_PART and self.number_of_parts is not None:
            raise ValueError(
                "number_of_parts should not be provided for 'single_part' mode"
            )
        return self

    def model_dump(self, **kwargs):
        kwargs.setdefault("mode", "json")
        data = super().model_dump(**kwargs)
        return {k: v for k, v in data.items() if v is not None}


class FileUploadSendData(BaseModel):
    file: bytes
    part_number: int | None = Field(None, ge=1)


class FileUploadCompleteRequest(BaseModel):
    pass


class FileUploadAttachment(BaseModel):
    file_upload: dict[str, str]
    name: str | None = None

    @classmethod
    def from_id(cls, file_upload_id: UUID, name: str | None = None):
        return cls(type="file_upload", file_upload={"id": file_upload_id}, name=name)


class FileUploadQuery(BaseModel):
    status: FileUploadStatus | None = None
    in_trash: bool | None = None

    page_size_limit: int | None = None
    total_results_limit: int | None = None

    @field_validator("page_size_limit")
    @classmethod
    def validate_page_size(cls, value: int | None) -> int | None:
        if value is None:
            return None
        return max(1, min(value, 100))

    @field_validator("total_results_limit")
    @classmethod
    def validate_total_results(cls, value: int | None) -> int:
        if value is None:
            return 100
        return max(1, value)

    @model_serializer
    def serialize_model(self) -> dict[str, str | bool | None]:
        result = {}

        if self.status is not None:
            result["status"] = self.status

        if self.in_trash is not None:
            result["in_trash"] = self.in_trash

        return result
