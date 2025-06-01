from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreatedBy(BaseModel):
    """Model for created_by field."""

    id: str
    type: str  # Usually "bot" in this case


class NumberOfParts(BaseModel):
    """Model for number_of_parts in multi-part uploads."""

    total: int = Field(..., description="Total number of parts for multi-part upload")


class NotionFileUploadResponse(BaseModel):
    """
    Pydantic model for Notion file upload responses.

    Covers both single-part and multi-part upload responses.
    """

    object: str = Field("file_upload", description="Always 'file_upload'")
    id: str = Field(..., description="Unique file upload ID")
    created_time: datetime = Field(..., description="When the upload was created")
    created_by: CreatedBy = Field(..., description="Who created the upload")
    last_edited_time: datetime = Field(..., description="When last edited")
    expiry_time: Optional[datetime] = Field(
        None, description="When the upload URL expires"
    )
    upload_url: Optional[str] = Field(
        None, description="Direct upload URL for single-part uploads"
    )
    archived: bool = Field(False, description="Whether the upload is archived")
    status: str = Field(..., description="Upload status (e.g., 'uploaded', 'pending')")
    filename: Optional[str] = Field(None, description="Original filename")
    content_type: Optional[str] = Field(None, description="MIME type of the file")
    content_length: Optional[int] = Field(None, description="Content length in bytes")
    request_id: str = Field(..., description="Request ID for this operation")

    # Multi-part upload specific fields
    mode: Optional[str] = Field(None, description="Upload mode (e.g., 'multi_part')")
    number_of_parts: Optional[NumberOfParts] = Field(
        None, description="Part information for multi-part uploads"
    )

    class Config:
        extra = "allow"  # Allow additional fields from the API
