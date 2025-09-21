from enum import Enum
from typing import Literal

from pydantic import BaseModel


class UploadMode(str, Enum):
    """Enum for file upload modes."""

    SINGLE_PART = "single_part"
    MULTI_PART = "multi_part"


class FileUploadResponse(BaseModel):
    """
    Represents a Notion file upload object as returned by the File Upload API.
    """

    object: Literal["file_upload"]
    id: str
    created_time: str
    last_edited_time: str
    expiry_time: str
    upload_url: str
    archived: bool
    status: str  # "pending", "uploaded", "failed", etc.
    filename: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    request_id: str


class FileUploadListResponse(BaseModel):
    """
    Response model for listing file uploads from /v1/file_uploads endpoint.
    """

    object: Literal["list"]
    results: list[FileUploadResponse]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["file_upload"]
    file_upload: dict = {}
    request_id: str


class FileUploadCreateRequest(BaseModel):
    """
    Request model for creating a file upload.
    """

    filename: str
    content_type: str | None = None
    content_length: int | None = None
    mode: UploadMode = UploadMode.SINGLE_PART

    def model_dump(self, **kwargs):
        """Override to exclude None values"""
        data = super().model_dump(**kwargs)
        return {k: v for k, v in data.items() if v is not None}


class FileUploadCompleteRequest(BaseModel):
    """
    Request model for completing a multi-part file upload.
    """

    # Usually empty for complete requests, but keeping for future extensibility
    pass
