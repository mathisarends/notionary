from __future__ import annotations

import asyncio
from typing import Self

from notionary.data_source.service import NotionDataSource
from notionary.database.database_factory import (
    load_database_from_id,
    load_database_from_title,
)
from notionary.database.database_http_client import NotionDatabaseHttpClient
from notionary.database.database_metadata_update_client import DatabaseMetadataUpdateClient
from notionary.shared.entity.entity import Entity


class NotionDatabase(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        last_edited_time: str,
        url: str,
        in_trash: bool,
        is_inline: bool,
        data_source_ids: list[str],
        public_url: str | None = None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(
            id=id,
            created_time=created_time,
            last_edited_time=last_edited_time,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._title = title
        self._url = url
        self._public_url = public_url
        self._description = description
        self._is_inline = is_inline

        self._data_sources: list[NotionDataSource] | None = None
        self._data_source_ids = data_source_ids

        self.client = NotionDatabaseHttpClient(database_id=id)

        self._metadata_update_client = DatabaseMetadataUpdateClient(database_id=id)

    @classmethod
    async def from_id(cls, id: str) -> Self:
        return await load_database_from_id(id)

    @classmethod
    async def from_title(
        cls,
        title: str,
    ) -> Self:
        return await load_database_from_title(title)

    @property
    def _entity_metadata_update_client(self) -> DatabaseMetadataUpdateClient:
        return self._metadata_update_client

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def public_url(self) -> str | None:
        return self._public_url

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def is_inline(self) -> bool:
        return self._is_inline

    async def get_data_sources(self) -> list[NotionDataSource]:
        if self._data_sources is None:
            self._data_sources = await self._load_data_sources()
        return self._data_sources

    async def _load_data_sources(self) -> list[NotionDataSource]:
        from notionary.data_source.service import NotionDataSource

        return await asyncio.gather(
            *(NotionDataSource.from_id(data_source_id) for data_source_id in self._data_source_ids)
        )

    async def set_title(self, title: str) -> None:
        result = await self.client.update_database_title(title=title)
        self._title = result.title[0].plain_text

    async def set_description(self, description: str) -> None:
        updated_description = await self.client.update_database_description(description=description)
        self._description = updated_description
