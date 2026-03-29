import logging
import random
from collections.abc import Sequence
from pathlib import Path

from notionary.file_upload import FileUploads
from notionary.http.client import HttpClient
from notionary.shared.object.dtos import NotionObjectResponseDto, NotionObjectUpdateDto
from notionary.shared.object.icon.schemas import AnyIcon, EmojiIcon
from notionary.shared.object.schemas import (
    ExternalFile,
    File,
    FileUploadedFileData,
    FileUploadFile,
    NotionHostedFile,
)

logger = logging.getLogger(__name__)


class NotionObject:
    """Manages icon, cover, and trash state for a Notion object.

    Consolidates the shared mutable properties that pages, databases,
    and data sources have in common, and sends them through a single
    PATCH endpoint.
    """

    _GRADIENT_COVERS: Sequence[str] = [
        f"https://www.notion.so/images/page-cover/gradients_{i}.png"
        for i in range(1, 10)
    ]

    def __init__(
        self,
        icon: AnyIcon | None,
        cover: File | None,
        in_trash: bool,
        http_client: HttpClient,
        path: str,
        file_uploads: FileUploads,
    ) -> None:
        self._http = http_client
        self._path = path
        self._file_uploads = file_uploads

        self.icon_emoji: str | None = self._extract_icon_emoji(icon)
        self.icon_url: str | None = self._extract_icon_url(icon)
        self.cover_url: str | None = self._extract_cover_url(cover)
        self.in_trash = in_trash

    # --- Icon -----------------------------------------------------------------

    async def set_icon_emoji(self, emoji: str) -> None:
        response = await self._patch(NotionObjectUpdateDto(icon=EmojiIcon(emoji=emoji)))
        self.icon_emoji = self._extract_icon_emoji(response.icon)
        self.icon_url = None

    async def set_icon_url(self, url: str) -> None:
        response = await self._patch(
            NotionObjectUpdateDto(icon=ExternalFile.from_url(url))
        )
        self.icon_emoji = None
        self.icon_url = self._extract_icon_url(response.icon)

    async def set_icon_from_file(self, file_path: Path | str) -> None:
        upload = await self._file_uploads.upload(Path(file_path), wait=True)
        icon = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(icon=icon))
        self.icon_emoji = None
        self.icon_url = None

    async def set_icon_from_bytes(self, content: bytes, filename: str) -> None:
        upload = await self._file_uploads.upload_from_bytes(
            content, filename, wait=True
        )
        icon = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(icon=icon))
        self.icon_emoji = None
        self.icon_url = None

    async def remove_icon(self) -> None:
        await self._patch(NotionObjectUpdateDto(icon=None))
        self.icon_emoji = None
        self.icon_url = None

    # --- Cover ----------------------------------------------------------------

    async def set_cover_url(self, url: str) -> None:
        response = await self._patch(
            NotionObjectUpdateDto(cover=ExternalFile.from_url(url))
        )
        self.cover_url = self._extract_cover_url(response.cover)

    async def set_random_cover(self) -> None:
        await self.set_cover_url(random.choice(self._GRADIENT_COVERS))

    async def set_cover_from_file(self, file_path: Path | str) -> None:
        upload = await self._file_uploads.upload(Path(file_path), wait=True)
        cover = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(cover=cover))
        self.cover_url = None

    async def set_cover_from_bytes(self, content: bytes, filename: str) -> None:
        upload = await self._file_uploads.upload_from_bytes(
            content, filename, wait=True
        )
        cover = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(cover=cover))
        self.cover_url = None

    async def remove_cover(self) -> None:
        await self._patch(NotionObjectUpdateDto(cover=None))
        self.cover_url = None

    # --- Trash ----------------------------------------------------------------

    async def trash(self) -> None:
        if self.in_trash:
            logger.warning("Entity is already in trash.")
            return
        response = await self._patch(NotionObjectUpdateDto(in_trash=True))
        self.in_trash = response.in_trash

    async def restore(self) -> None:
        if not self.in_trash:
            logger.warning("Entity is not in trash.")
            return
        response = await self._patch(NotionObjectUpdateDto(in_trash=False))
        self.in_trash = response.in_trash

    # --- Batch update ---------------------------------------------------------

    async def update(
        self,
        *,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        cover_url: str | None = None,
    ) -> None:
        dto = NotionObjectUpdateDto()
        if icon_emoji is not None:
            dto.icon = EmojiIcon(emoji=icon_emoji)
        elif icon_url is not None:
            dto.icon = ExternalFile.from_url(icon_url)
        if cover_url is not None:
            dto.cover = ExternalFile.from_url(cover_url)

        if dto.icon is None and dto.cover is None:
            return

        response = await self._patch(dto)
        self.icon_emoji = self._extract_icon_emoji(response.icon)
        self.icon_url = self._extract_icon_url(response.icon)
        self.cover_url = self._extract_cover_url(response.cover)

    # --- Internal -------------------------------------------------------------

    async def _patch(self, dto: NotionObjectUpdateDto) -> NotionObjectResponseDto:
        response = await self._http.patch(self._path, data=dto, exclude_unset=True)
        return NotionObjectResponseDto.model_validate(response)

    @staticmethod
    def _extract_icon_emoji(icon: AnyIcon | None) -> str | None:
        return icon.emoji if isinstance(icon, EmojiIcon) else None

    @staticmethod
    def _extract_icon_url(icon: AnyIcon | None) -> str | None:
        if isinstance(icon, ExternalFile):
            return icon.external.url
        if isinstance(icon, NotionHostedFile):
            return icon.file.url
        return None

    @staticmethod
    def _extract_cover_url(cover: File | None) -> str | None:
        if cover is None:
            return None
        return cover.get_url()
