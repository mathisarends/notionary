from pathlib import Path

from notionary.file_upload import Files
from notionary.http.client import HttpClient
from notionary.shared.object.dtos import NotionObjectResponseDto, NotionObjectUpdateDto
from notionary.shared.object.icon.schemas import AnyIcon, EmojiIcon
from notionary.shared.object.schemas import (
    ExternalFile,
    FileUploadedFileData,
    FileUploadFile,
    NotionHostedFile,
)


class Icon:
    def __init__(
        self,
        icon: AnyIcon | None,
        http_client: HttpClient,
        path: str,
        file_uploads: Files,
    ) -> None:
        self._http = http_client
        self._path = path
        self._file_uploads = file_uploads
        self.emoji: str | None = self._extract_emoji(icon)
        self.external_url: str | None = self._extract_external_url(icon)

    async def set_emoji(self, emoji: str) -> None:
        response = await self._patch(NotionObjectUpdateDto(icon=EmojiIcon(emoji=emoji)))
        self.emoji = self._extract_emoji(response.icon)
        self.external_url = None

    async def set_from_url(self, url: str) -> None:
        response = await self._patch(
            NotionObjectUpdateDto(icon=ExternalFile.from_url(url))
        )
        self.emoji = None
        self.external_url = self._extract_external_url(response.icon)

    async def set_from_file(self, file_path: Path | str) -> None:
        upload = await self._file_uploads.upload(Path(file_path), wait=True)
        icon = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(icon=icon))
        self.emoji = None
        self.external_url = None

    async def set_from_bytes(self, content: bytes, filename: str) -> None:
        upload = await self._file_uploads.upload_from_bytes(
            content, filename, wait=True
        )
        icon = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(icon=icon))
        self.emoji = None
        self.external_url = None

    async def remove(self) -> None:
        await self._patch(NotionObjectUpdateDto(icon=None))
        self.emoji = None
        self.external_url = None

    async def _patch(self, dto: NotionObjectUpdateDto) -> NotionObjectResponseDto:
        data = dto.model_dump(exclude_unset=True, exclude_none=True)
        response = await self._http.patch(self._path, data=data)
        return NotionObjectResponseDto.model_validate(response)

    @staticmethod
    def _extract_emoji(icon: AnyIcon | None) -> str | None:
        return icon.emoji if isinstance(icon, EmojiIcon) else None

    @staticmethod
    def _extract_external_url(icon: AnyIcon | None) -> str | None:
        if isinstance(icon, ExternalFile):
            return icon.external.url
        if isinstance(icon, NotionHostedFile):
            return icon.file.url
        return None
