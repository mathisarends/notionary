from pathlib import Path
from typing import ClassVar, override

from notionary.exceptions.file_upload import NoFileExtensionException, UnsupportedFileTypeException
from notionary.file_upload.schemas import (
    AudioExtension,
    AudioMimeType,
    DocumentExtension,
    DocumentMimeType,
    FileCategory,
    ImageExtension,
    ImageMimeType,
    VideoExtension,
    VideoMimeType,
)
from notionary.file_upload.validation.port import FileUploadValidator


class FileExtensionValidator(FileUploadValidator):
    EXTENSION_TO_MIME: ClassVar[dict[str, str]] = {
        AudioExtension.AAC: AudioMimeType.AAC,
        AudioExtension.ADTS: AudioMimeType.AAC,
        AudioExtension.MID: AudioMimeType.MIDI,
        AudioExtension.MIDI: AudioMimeType.MIDI,
        AudioExtension.MP3: AudioMimeType.MPEG,
        AudioExtension.MPGA: AudioMimeType.MPEG,
        AudioExtension.M4A: AudioMimeType.MP4,
        AudioExtension.M4B: AudioMimeType.MP4,
        AudioExtension.MP4: AudioMimeType.MP4,
        AudioExtension.OGA: AudioMimeType.OGG,
        AudioExtension.OGG: AudioMimeType.OGG,
        AudioExtension.WAV: AudioMimeType.WAV,
        AudioExtension.WMA: AudioMimeType.WMA,
        DocumentExtension.PDF: DocumentMimeType.PDF,
        DocumentExtension.TXT: DocumentMimeType.PLAIN_TEXT,
        DocumentExtension.JSON: DocumentMimeType.JSON,
        DocumentExtension.DOC: DocumentMimeType.MSWORD,
        DocumentExtension.DOT: DocumentMimeType.MSWORD,
        DocumentExtension.DOCX: DocumentMimeType.WORD_DOCUMENT,
        DocumentExtension.DOTX: DocumentMimeType.WORD_TEMPLATE,
        DocumentExtension.XLS: DocumentMimeType.EXCEL,
        DocumentExtension.XLT: DocumentMimeType.EXCEL,
        DocumentExtension.XLA: DocumentMimeType.EXCEL,
        DocumentExtension.XLSX: DocumentMimeType.EXCEL_SHEET,
        DocumentExtension.XLTX: DocumentMimeType.EXCEL_TEMPLATE,
        DocumentExtension.PPT: DocumentMimeType.POWERPOINT,
        DocumentExtension.POT: DocumentMimeType.POWERPOINT,
        DocumentExtension.PPS: DocumentMimeType.POWERPOINT,
        DocumentExtension.PPA: DocumentMimeType.POWERPOINT,
        DocumentExtension.PPTX: DocumentMimeType.POWERPOINT_PRESENTATION,
        DocumentExtension.POTX: DocumentMimeType.POWERPOINT_TEMPLATE,
        ImageExtension.GIF: ImageMimeType.GIF,
        ImageExtension.HEIC: ImageMimeType.HEIC,
        ImageExtension.JPEG: ImageMimeType.JPEG,
        ImageExtension.JPG: ImageMimeType.JPEG,
        ImageExtension.PNG: ImageMimeType.PNG,
        ImageExtension.SVG: ImageMimeType.SVG,
        ImageExtension.TIF: ImageMimeType.TIFF,
        ImageExtension.TIFF: ImageMimeType.TIFF,
        ImageExtension.WEBP: ImageMimeType.WEBP,
        ImageExtension.ICO: ImageMimeType.ICON,
        VideoExtension.AMV: VideoMimeType.AMV,
        VideoExtension.ASF: VideoMimeType.ASF,
        VideoExtension.WMV: VideoMimeType.ASF,
        VideoExtension.AVI: VideoMimeType.AVI,
        VideoExtension.F4V: VideoMimeType.F4V,
        VideoExtension.FLV: VideoMimeType.FLV,
        VideoExtension.GIFV: VideoMimeType.WEBM,
        VideoExtension.M4V: VideoMimeType.MP4,
        VideoExtension.MP4: VideoMimeType.MP4,
        VideoExtension.MKV: VideoMimeType.MKV,
        VideoExtension.WEBM: VideoMimeType.WEBM,
        VideoExtension.MOV: VideoMimeType.QUICKTIME,
        VideoExtension.QT: VideoMimeType.QUICKTIME,
        VideoExtension.MPEG: VideoMimeType.MPEG,
    }

    EXTENSION_TO_CATEGORY: ClassVar[dict[str, FileCategory]] = {
        **{ext.value: FileCategory.AUDIO for ext in AudioExtension},
        **{ext.value: FileCategory.DOCUMENT for ext in DocumentExtension},
        **{ext.value: FileCategory.IMAGE for ext in ImageExtension},
        **{ext.value: FileCategory.VIDEO for ext in VideoExtension},
    }

    def __init__(self, filename: str | Path) -> None:
        self.filename = Path(filename).name if isinstance(filename, Path) else filename

    @override
    async def validate(self) -> None:
        extension = self._extract_extension(self.filename)

        if not extension:
            raise NoFileExtensionException(self.filename)

        if not self._is_supported(extension):
            supported_by_category = self._get_supported_extensions_by_category()
            raise UnsupportedFileTypeException(extension, self.filename, supported_by_category)

    @staticmethod
    def _extract_extension(filename: str) -> str:
        import os

        _, ext = os.path.splitext(filename)
        return ext.lower()

    def _is_supported(self, extension: str) -> bool:
        normalized = self._normalize_extension(extension)
        return normalized in self.EXTENSION_TO_MIME

    @staticmethod
    def _normalize_extension(extension: str) -> str:
        extension = extension.lower()
        if not extension.startswith("."):
            extension = f".{extension}"
        return extension

    def _get_supported_extensions_by_category(self) -> dict[str, list[str]]:
        result = {}
        for category in FileCategory:
            extensions = [ext for ext, cat in self.EXTENSION_TO_CATEGORY.items() if cat == category]
            result[category.value] = extensions
        return result
