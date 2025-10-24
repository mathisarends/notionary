from dataclasses import dataclass


@dataclass(frozen=True)
class FileUploadConfig:
    """Configuration for Notion File Upload API.

    Based on official Notion API documentation:
    https://developers.notion.com/reference/file-uploads
    """

    TWENTY_MEGABYTES = 20 * 1024 * 1024
    SINGLE_PART_MAX_SIZE = TWENTY_MEGABYTES

    # Valid range: 5-20 MB per part (last part can be < 5 MB)
    # Notion explicitly recommends 10 MB for optimal performance
    TEN_MEGABYTES = 10 * 1024 * 1024
    MULTI_PART_CHUNK_SIZE = TEN_MEGABYTES

    MAX_FILENAME_BYTES: int = 900

    MAX_UPLOAD_TIMEOUT: int = 300
    POLL_INTERVAL: int = 2
