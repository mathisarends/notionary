from typing import Any
from uuid import UUID

from notionary.database.schemas import (
    CreateDatabaseRequest,
    DatabaseDto,
    UpdateDatabaseRequest,
)
from notionary.http.client import HttpClient
from notionary.rich_text import markdown_to_rich_text
from notionary.shared.object.icon.schemas import EmojiIcon
from notionary.shared.object.schemas import ExternalFile


class DatabaseHttpClient:
    _ENDPOINT = "databases"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def retrieve(self, database_id: UUID) -> DatabaseDto:
        response = await self._http.get(f"{self._ENDPOINT}/{database_id}")
        return DatabaseDto.model_validate(response)

    async def create(
        self,
        parent_page_id: UUID | None = None,
        title: str | None = None,
        description: str | None = None,
        is_inline: bool | None = None,
        initial_properties: dict[str, Any] | None = None,
        icon_emoji: str | None = None,
        cover_url: str | None = None,
    ) -> DatabaseDto:
        if parent_page_id:
            parent = {"type": "page_id", "page_id": parent_page_id}
        else:
            parent = {"type": "workspace", "workspace": True}

        request = CreateDatabaseRequest(parent=parent)

        if title:
            request.title = markdown_to_rich_text(title)
        if description:
            request.description = markdown_to_rich_text(description)
        if is_inline is not None:
            request.is_inline = is_inline
        if initial_properties:
            request.initial_data_source = {"properties": initial_properties}
        if icon_emoji:
            request.icon = EmojiIcon(emoji=icon_emoji).model_dump(mode="json")
        if cover_url:
            request.cover = ExternalFile.from_url(cover_url).model_dump(mode="json")

        response = await self._http.post(self._ENDPOINT, data=request)
        return DatabaseDto.model_validate(response)

    async def update(
        self, database_id: UUID, update: UpdateDatabaseRequest
    ) -> DatabaseDto:
        response = await self._http.patch(
            f"{self._ENDPOINT}/{database_id}", data=update
        )
        return DatabaseDto.model_validate(response)
