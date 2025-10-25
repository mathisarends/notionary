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


# ============================================================================
# AUDIO
# ============================================================================


class AudioExtension(StrEnum):
    AAC = ".aac"
    ADTS = ".adts"
    MID = ".mid"
    MIDI = ".midi"
    MP3 = ".mp3"
    MPGA = ".mpga"
    M4A = ".m4a"
    M4B = ".m4b"
    MP4 = ".mp4"
    OGA = ".oga"
    OGG = ".ogg"
    WAV = ".wav"
    WMA = ".wma"


class AudioMimeType(StrEnum):
    AAC = "audio/aac"
    MIDI = "audio/midi"
    MPEG = "audio/mpeg"
    MP4 = "audio/mp4"
    OGG = "audio/ogg"
    WAV = "audio/wav"
    WMA = "audio/x-ms-wma"


# ============================================================================
# DOCUMENT
# ============================================================================


class DocumentExtension(StrEnum):
    PDF = ".pdf"
    TXT = ".txt"
    JSON = ".json"
    DOC = ".doc"
    DOT = ".dot"
    DOCX = ".docx"
    DOTX = ".dotx"
    XLS = ".xls"
    XLT = ".xlt"
    XLA = ".xla"
    XLSX = ".xlsx"
    XLTX = ".xltx"
    PPT = ".ppt"
    POT = ".pot"
    PPS = ".pps"
    PPA = ".ppa"
    PPTX = ".pptx"
    POTX = ".potx"


class DocumentMimeType(StrEnum):
    PDF = "application/pdf"
    PLAIN_TEXT = "text/plain"
    JSON = "application/json"
    MSWORD = "application/msword"
    WORD_DOCUMENT = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    WORD_TEMPLATE = "application/vnd.openxmlformats-officedocument.wordprocessingml.template"
    EXCEL = "application/vnd.ms-excel"
    EXCEL_SHEET = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXCEL_TEMPLATE = "application/vnd.openxmlformats-officedocument.spreadsheetml.template"
    POWERPOINT = "application/vnd.ms-powerpoint"
    POWERPOINT_PRESENTATION = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    POWERPOINT_TEMPLATE = "application/vnd.openxmlformats-officedocument.presentationml.template"


# ============================================================================
# IMAGE
# ============================================================================


class ImageExtension(StrEnum):
    GIF = ".gif"
    HEIC = ".heic"
    JPEG = ".jpeg"
    JPG = ".jpg"
    PNG = ".png"
    SVG = ".svg"
    TIF = ".tif"
    TIFF = ".tiff"
    WEBP = ".webp"
    ICO = ".ico"


class ImageMimeType(StrEnum):
    GIF = "image/gif"
    HEIC = "image/heic"
    JPEG = "image/jpeg"
    PNG = "image/png"
    SVG = "image/svg+xml"
    TIFF = "image/tiff"
    WEBP = "image/webp"
    ICON = "image/vnd.microsoft.icon"


# ============================================================================
# VIDEO
# ============================================================================


class VideoExtension(StrEnum):
    AMV = ".amv"
    ASF = ".asf"
    WMV = ".wmv"
    AVI = ".avi"
    F4V = ".f4v"
    FLV = ".flv"
    GIFV = ".gifv"
    M4V = ".m4v"
    MP4 = ".mp4"
    MKV = ".mkv"
    WEBM = ".webm"
    MOV = ".mov"
    QT = ".qt"
    MPEG = ".mpeg"


class VideoMimeType(StrEnum):
    AMV = "video/x-amv"
    ASF = "video/x-ms-asf"
    AVI = "video/x-msvideo"
    F4V = "video/x-f4v"
    FLV = "video/x-flv"
    MP4 = "video/mp4"
    MKV = "video/x-matroska"
    WEBM = "video/webm"
    QUICKTIME = "video/quicktime"
    MPEG = "video/mpeg"


# ============================================================================
# CATEGORY
# ============================================================================


class FileCategory(StrEnum):
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
