from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from notionary.database.database_factory import (
    load_database_from_id,
    load_database_from_title,
)
from notionary.database.database_filter_builder import DatabaseFilterBuilder
from notionary.database.database_http_client import NotionDatabseHttpClient
from notionary.database.database_metadata_update_client import DatabaseMetadataUpdateClient
from notionary.database.database_models import (
    NotionQueryDatabaseResponse,
)
from notionary.database.properties.database_property_models import (
    DatabaseNotionProperty,
)
from notionary.database.properties.database_property_reader import DatabasePropertyReader
from notionary.page.page import NotionPage
from notionary.page.page_models import NotionPageDto
from notionary.shared.entities.entity import NotionEntity
from notionary.shared.entities.entity_metadata_update_client import EntityMetadataUpdateClient


class NotionDatabase(NotionEntity):
    def __init__(
        self,
        id: str,
        title: str,
        url: str,
        archived: bool,
        in_trash: bool,
        is_inline: bool,
        emoji_icon: str | any | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        properties: dict[str, DatabaseNotionProperty] | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(
            id=id,
            title=title,
            url=url,
            archived=archived,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
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

    async def query_database_by_title(self, page_title: str) -> list[NotionPage]:
        search_results: NotionQueryDatabaseResponse = await self.client.query_database_by_title(page_title=page_title)

        page_results: list[NotionPage] = []

        if search_results.results:
            page_tasks = [NotionPage.from_id(page_response.id) for page_response in search_results.results]
            page_results = await asyncio.gather(*page_tasks)

        return page_results

    async def iter_pages_updated_within(self, hours: int = 24, page_size: int = 100) -> AsyncGenerator[NotionPage]:
        filter_builder = DatabaseFilterBuilder()
        filter_builder.with_updated_last_n_hours(hours)
        filter_conditions = filter_builder.build()

        async for page in self._iter_pages(page_size, filter_conditions):
            yield page

    async def get_all_pages(self) -> list[NotionPage]:
        pages: list[NotionPage] = []

        async for batch in self._paginate_database(page_size=100):
            page_tasks = [NotionPage.from_id(page_response.id) for page_response in batch]
            batch_pages = await asyncio.gather(*page_tasks)
            pages.extend(batch_pages)

        return pages

    async def get_last_edited_time(self) -> str:
        db = await self.client.get_database(self.id)
        return db.last_edited_time

    async def _iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: dict[str, Any] | None = None,
    ) -> AsyncGenerator[NotionPage]:
        """
        Asynchronous generator that yields NotionPage objects from the database.
        """
        async for batch in self._paginate_database(page_size, filter_conditions):
            for page_response in batch:
                yield await NotionPage.from_id(page_response.id)

    async def _paginate_database(
        self,
        page_size: int = 100,
        filter_conditions: dict[str, Any] | None = None,
    ) -> AsyncGenerator[list[NotionPageDto]]:
        """
        Central pagination logic for Notion Database queries.
        """
        start_cursor: str | None = None
        has_more = True

        while has_more:
            query_data: dict[str, Any] = {"page_size": page_size}

            if start_cursor:
                query_data["start_cursor"] = start_cursor
            if filter_conditions:
                query_data["filter"] = filter_conditions

            result: NotionQueryDatabaseResponse = await self.client.query_database(query_data=query_data)

            if not result or not result.results:
                return

            yield result.results

            has_more = result.has_more
            start_cursor = result.next_cursor if has_more else None
