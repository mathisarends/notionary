from enum import StrEnum


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
    WORD_DOCUMENT = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    WORD_TEMPLATE = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.template"
    )
    EXCEL = "application/vnd.ms-excel"
    EXCEL_SHEET = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXCEL_TEMPLATE = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.template"
    )
    POWERPOINT = "application/vnd.ms-powerpoint"
    POWERPOINT_PRESENTATION = (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    POWERPOINT_TEMPLATE = (
        "application/vnd.openxmlformats-officedocument.presentationml.template"
    )


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


class FileCategory(StrEnum):
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
