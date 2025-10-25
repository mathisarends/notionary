from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class UploadMode(StrEnum):
    SINGLE_PART = "single_part"
    MULTI_PART = "multi_part"


class FileUploadStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"
    EXPIRED = "expired"


class FileUploadResponse(BaseModel):
    id: str
    created_time: str
    last_edited_time: str
    expiry_time: str | None = None
    upload_url: str | None = None
    archived: bool
    status: FileUploadStatus
    filename: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    request_id: str | None = None


class FileUploadFilter(BaseModel):
    status: FileUploadStatus | None = None
    archived: bool | None = None


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
            raise ValueError("number_of_parts should not be provided for 'single_part' mode")
        return self

    def model_dump(self, **kwargs):
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
    def from_id(cls, file_upload_id: str, name: str | None = None):
        return cls(type="file_upload", file_upload={"id": file_upload_id}, name=name)
