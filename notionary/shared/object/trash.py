import logging

from notionary.http.client import HttpClient
from notionary.shared.object.dtos import NotionObjectResponseDto, NotionObjectUpdateDto

logger = logging.getLogger(__name__)


class Trash:
    def __init__(
        self,
        in_trash: bool,
        http_client: HttpClient,
        path: str,
    ) -> None:
        self._http = http_client
        self._path = path
        self.in_trash = in_trash

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

    async def _patch(self, dto: NotionObjectUpdateDto) -> NotionObjectResponseDto:
        data = dto.model_dump(exclude_unset=True, exclude_none=True)
        response = await self._http.patch(self._path, data=data)
        return NotionObjectResponseDto.model_validate(response)
