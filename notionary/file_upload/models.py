from typing import List, Literal, Optional

from pydantic import BaseModel


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
    filename: Optional[str] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    request_id: str


class FileUploadListResponse(BaseModel):
    """
    Response model for listing file uploads from /v1/file_uploads endpoint.
    """

    object: Literal["list"]
    results: List[FileUploadResponse]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["file_upload"]
    file_upload: dict = {}
    request_id: str


class FileUploadCreateRequest(BaseModel):
    """
    Request model for creating a file upload.
    """

    filename: str
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    mode: Literal["single_part", "multi_part"] = "single_part"

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
