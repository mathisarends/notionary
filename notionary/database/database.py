from __future__ import annotations

from notionary.database.database_factory import (
    load_database_from_id,
    load_database_from_title,
)
from notionary.database.database_filter_builder import DatabaseFilterBuilder
from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.database.database_metadata_update_client import DatabaseMetadataUpdateClient
from notionary.database.properties.database_property_models import (
    DatabaseNotionProperty,
)
from notionary.database.properties.database_property_reader import DatabasePropertyReader
from notionary.page.page import NotionPage
from notionary.page.page_models import NotionPageDto
from notionary.shared.entities.entity import NotionEntity
from notionary.shared.entities.entity_metadata_update_client import EntityMetadataUpdateClient
from notionary.shared.models.user_models import NotionUser


class NotionDatabase(NotionEntity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        created_by: NotionUser,
        last_edited_time: str,
        last_edited_by: NotionUser,
        url: str,
        archived: bool,
        in_trash: bool,
        is_inline: bool,
        public_url: str | None = None,
        emoji_icon: str | any | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        properties: dict[str, DatabaseNotionProperty] | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(
            id=id,
            title=title,
            created_time=created_time,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
            url=url,
            archived=archived,
            in_trash=in_trash,
            public_url=public_url,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
            created_by=created_by,
        )
        self._properties = properties or {}
        self._description = description
        self._is_inline = is_inline

        self.client = NotionDatabseHttpClient(database_id=id)

        self._metadata_update_client = DatabaseMetadataUpdateClient(database_id=id)
        self.property_reader = DatabasePropertyReader(self)

    @classmethod
    async def from_id(cls, id: str) -> NotionDatabase:
        return await load_database_from_id(id)

    @classmethod
    async def from_title(
        cls,
        title: str,
        min_similarity: float = 0.6,
    ) -> NotionDatabase:
        return await load_database_from_title(title, min_similarity)

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def is_inline(self) -> bool:
        return self._is_inline

    @property
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient:
        return self._metadata_update_client

    @property
    def properties(self) -> dict[str, DatabaseNotionProperty]:
        return self._properties

    async def create_blank_page(self) -> NotionPage:
        create_page_response: NotionPageDto = await self.client.create_page()

        return await NotionPage.from_id(create_page_response.id)

    async def set_title(self, title: str) -> None:
        result = await self.client.update_database_title(title=title)
        self._title = result.title[0].plain_text

    async def set_description(self, description: str) -> None:
        udapted_description = await self.client.update_database_description(description=description)
        self._description = udapted_description

    def filter(self) -> DatabaseFilterBuilder:
        return DatabaseFilterBuilder(database=self)

    async def find_by_title(self, title: str) -> list[NotionPage]:
        return await self.filter().title_contains(title).to_list()

    async def all_pages(self, page_size: int = 100) -> list[NotionPage]:
        return await self.filter().page_size(page_size).to_list()
