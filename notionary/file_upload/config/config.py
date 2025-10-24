from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from notionary.file_upload.config.constants import (
    NOTION_MULTI_PART_CHUNK_SIZE_MAX,
    NOTION_MULTI_PART_CHUNK_SIZE_MIN,
    NOTION_RECOMMENDED_CHUNK_SIZE,
)


class FileUploadConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    multi_part_chunk_size: int = Field(
        default=NOTION_RECOMMENDED_CHUNK_SIZE,
        ge=NOTION_MULTI_PART_CHUNK_SIZE_MIN,
        le=NOTION_MULTI_PART_CHUNK_SIZE_MAX,
        description=(
            "The part size (in bytes) for multi-part uploads. Must be within Notion's allowed range (e.g., 5MB-20MB)."
        ),
    )

    max_upload_timeout: int = Field(
        default=300, gt=0, description="Maximum time in seconds to wait for an upload to complete."
    )

    poll_interval: int = Field(default=2, gt=0, description="Interval in seconds for polling the upload status.")

    base_upload_path: Path | None = Field(
        default=None, description="Optional default base path for resolving relative file uploads."
    )
