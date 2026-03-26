import random
from collections.abc import Sequence

from notionary.http.client import HttpClient
from notionary.shared.entity.schemas import EntityResponseDto, NotionEntityUpdateDto
from notionary.shared.models.file import ExternalFile, File


class EntityCover:
    _GRADIENT_COVERS: Sequence[str] = [
        f"https://www.notion.so/images/page-cover/gradients_{i}.png"
        for i in range(1, 10)
    ]

    def __init__(
        self,
        cover: File | None,
        http_client: HttpClient,
        path: str,
    ) -> None:
        self._http = http_client
        self._path = path
        self.url: str | None = self._extract_url(cover)

    async def set_from_url(self, image_url: str) -> None:
        response = await self._patch(
            NotionEntityUpdateDto(cover=ExternalFile.from_url(image_url))
        )
        self.url = self._extract_url(response.cover)

    async def set_random_gradient(self) -> None:
        await self.set_from_url(random.choice(self._GRADIENT_COVERS))

    async def remove(self) -> None:
        await self._patch(NotionEntityUpdateDto(cover=None))
        self.url = None

    async def _patch(self, dto: NotionEntityUpdateDto) -> EntityResponseDto:
        data = dto.model_dump(exclude_unset=True, exclude_none=True)
        response = await self._http.patch(self._path, data=data)
        return EntityResponseDto.model_validate(response)

    @staticmethod
    def _extract_url(cover: File | None) -> str | None:
        if cover is None:
            return None
        return cover.get_url()
