from __future__ import annotations

import asyncio
import random
from typing import Any, AsyncGenerator

from notionary.database.database_client import NotionDatabaseClient
from notionary.database.database_filter_builder import DatabaseFilterBuilder
from notionary.database.database_provider import NotionDatabaseProvider
from notionary.database.database_models import (
    NoionDatabaseDto,
    NotionQueryDatabaseResponse,
)
from notionary.page.page_models import NotionPageDto
from notionary.page.page import NotionPage
from notionary.shared.models.icon_models import IconType
from notionary.shared.models.database_property_models import (
    DatabaseNotionProperty,
    DatabasePropertyT,
    DatabaseStatusProperty,
    DatabaseMultiSelectProperty,
    DatabaseSelectProperty,
    DatabaseRelationProperty,
)
from notionary.page.properties.page_property_models import (
    PageTitleProperty,
)
from notionary.shared.models.shared_property_models import PropertyType
from notionary.util import LoggingMixin
from notionary.util.covers import get_random_gradient_cover


class NotionDatabase(LoggingMixin):
    def __init__(
        self,
        id: str,
        title: str,
        url: str,
        emoji_icon: str | any = None,
        properties: dict[str, DatabaseNotionProperty] | None = None,
        token: str | None = None,
    ):
        self._id = id
        self._title = title
        self._url = url
        self._emoji_icon = emoji_icon
        self._properties = properties or {}
        self.token = token

        self.client = NotionDatabaseClient(token=token)

    @classmethod
    async def from_database_id(
        cls, id: str, token: str | None = None
    ) -> NotionDatabase:
        provider = cls.get_database_provider()
        return await provider.get_database_by_id(id, token)

    @classmethod
    async def from_database_name(
        cls,
        database_name: str,
        token: str | None = None,
        min_similarity: float = 0.6,
    ) -> NotionDatabase:
        provider = cls.get_database_provider()
        return await provider.get_database_by_name(database_name, token, min_similarity)

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def emoji(self) -> str | None:
        return self._emoji_icon

    @property
    def properties(self) -> dict[str, DatabaseNotionProperty]:
        return self._properties

    @property
    def database_provider(self) -> NotionDatabaseProvider:
        return NotionDatabaseProvider.get_instance()

    @classmethod
    def get_database_provider(cls) -> NotionDatabaseProvider:
        return NotionDatabaseProvider.get_instance()

    async def create_blank_page(self) -> NotionPage:
        """
        Create a new blank page in the database with minimal properties.
        """
        create_page_response: NotionPageDto = await self.client.create_page(
            parent_database_id=self.id
        )

        return await NotionPage.from_page_id(
            page_id=create_page_response.id, token=self.token
        )

    async def set_title(self, new_title: str) -> str:
        result = await self.client.update_database_title(
            database_id=self.id, title=new_title
        )

        self._title = result.title[0].plain_text
        self.database_provider.invalidate_database_cache(database_id=self.id)
        return self._title

    async def set_emoji(self, new_emoji: str) -> str:
        """
        Update the database emoji.
        """
        result = await self.client.update_database_emoji(
            database_id=self.id, emoji=new_emoji
        )

        self._emoji_icon = result.icon.emoji if result.icon else None
        self.database_provider.invalidate_database_cache(database_id=self.id)
        return self._emoji_icon

    async def set_cover_image(self, image_url: str) -> str:
        result = await self.client.update_database_cover_image(
            database_id=self.id, image_url=image_url
        )

        self.database_provider.invalidate_database_cache(database_id=self.id)
        return (
            result.cover.external.url
            if result.cover and result.cover.external
            else image_url
        )

    async def set_random_gradient_cover(self) -> str:
        random_cover_url = get_random_gradient_cover()
        return await self.set_cover_image(random_cover_url)

    async def set_external_icon(self, external_icon_url: str) -> str:
        result = await self.client.update_database_external_icon(
            database_id=self.id, icon_url=external_icon_url
        )

        self.database_provider.invalidate_database_cache(database_id=self.id)
        return (
            result.icon.external.url
            if result.icon and result.icon.external
            else external_icon_url
        )

    async def get_property_options(self, property_name: str) -> list[str]:
        """
        Get the available options for a property (select, multi_select, status, relation).
        Returns empty list if property doesn't exist or has no options.
        """
        prop = self._properties.get(property_name)

        if not prop:
            return []

        if prop.type in (
            PropertyType.SELECT,
            PropertyType.MULTI_SELECT,
            PropertyType.STATUS,
        ):
            return prop.option_names
        elif prop.type == PropertyType.RELATION:
            return await self._get_relation_options(prop)

        return []

    # Keep the old method name for backward compatibility
    async def get_options_by_property_name(self, property_name: str) -> list[str]:
        """
        Retrieve all option names for a select, multi_select, status, or relation property.
        (Backward compatibility method - use get_property_options instead)
        """
        return await self.get_property_options(property_name)

    def get_property_type(self, property_name: str) -> str | None:
        """
        Get the type of a property by its name.
        """
        prop = self._properties.get(property_name)
        if not prop:
            return None

        if isinstance(prop, dict):
            return prop.get("type")

        return prop.type

    def get_status_property(self, property_name: str) -> DatabaseStatusProperty | None:
        """Get a status property by name with type safety."""
        return self._get_database_property(property_name, DatabaseStatusProperty)

    def get_select_property(self, property_name: str) -> DatabaseSelectProperty | None:
        """Get a select property by name with type safety."""
        return self._get_database_property(property_name, DatabaseSelectProperty)

    def get_multi_select_property(
        self, property_name: str
    ) -> DatabaseMultiSelectProperty | None:
        """Get a multi-select property by name with type safety."""
        return self._get_database_property(property_name, DatabaseMultiSelectProperty)

    def get_relation_property(
        self, property_name: str
    ) -> DatabaseRelationProperty | None:
        """Get a relation property by name with type safety."""
        return self._get_database_property(property_name, DatabaseRelationProperty)

    async def query_database_by_title(self, page_title: str) -> list[NotionPage]:
        """
        Query the database for pages with a specific title.
        """
        search_results: NotionQueryDatabaseResponse = (
            await self.client.query_database_by_title(
                database_id=self.id, page_title=page_title
            )
        )

        page_results: list[NotionPage] = []

        if search_results.results:
            page_tasks = [
                NotionPage.from_page_id(
                    page_id=page_response.id, token=self.client.token
                )
                for page_response in search_results.results
            ]
            page_results = await asyncio.gather(*page_tasks)

        return page_results

    async def iter_pages_updated_within(
        self, hours: int = 24, page_size: int = 100
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Iterate through pages edited in the last N hours using DatabaseFilterBuilder.
        """
        filter_builder = DatabaseFilterBuilder()
        filter_builder.with_updated_last_n_hours(hours)
        filter_conditions = filter_builder.build()

        async for page in self._iter_pages(page_size, filter_conditions):
            yield page

    async def get_all_pages(self) -> list[NotionPage]:
        """
        Get all pages in the database (use with caution for large databases).
        Uses asyncio.gather to parallelize NotionPage creation per API batch.
        """
        pages: list[NotionPage] = []

        async for batch in self._paginate_database(page_size=100):
            page_tasks = [
                NotionPage.from_page_id(
                    page_id=page_response.id, token=self.client.token
                )
                for page_response in batch
            ]
            batch_pages = await asyncio.gather(*page_tasks)
            pages.extend(batch_pages)

        return pages

    async def get_last_edited_time(self) -> str:
        """
        Retrieve the last edited time of the database.
        Returns ISO 8601 timestamp string of the last database edit.
        """
        db = await self.client.get_database(self.id)
        return db.last_edited_time

    async def _iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: dict[str, Any] | None = None,
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Asynchronous generator that yields NotionPage objects from the database.
        """
        async for batch in self._paginate_database(page_size, filter_conditions):
            for page_response in batch:
                yield await NotionPage.from_page_id(
                    page_id=page_response.id, token=self.client.token
                )

    async def _get_relation_options(
        self, relation_prop: DatabaseRelationProperty
    ) -> list[str]:
        """
        Get the titles of all pages related to a relation property.
        """
        related_db_id = relation_prop.related_database_id
        if not related_db_id:
            return []

        search_results = await self.client.query_database(database_id=related_db_id)

        page_titles = []
        for page_response in search_results.results:
            title = self._extract_title_from_page(page_response)
            if title:
                page_titles.append(title)

        return page_titles

    def _extract_title_from_page(self, page: NotionPageDto) -> str | None:
        """
        Extract the title from a NotionPageDto object using typed properties.
        """
        if not page.properties:
            return None

        title_property = next(
            (
                prop
                for prop in page.properties.values()
                if isinstance(prop, PageTitleProperty)
            ),
            None,
        )

        if not title_property:
            # Fallback to old method for backward compatibility
            title_property = next(
                (
                    prop
                    for prop in page.properties.values()
                    if isinstance(prop, dict) and prop.get("type") == "title"
                ),
                None,
            )

            if not title_property or "title" not in title_property:
                return None

            try:
                title_parts = title_property["title"]
                return "".join(part.get("plain_text", "") for part in title_parts)
            except (KeyError, TypeError, AttributeError):
                return None

        return "".join(item.plain_text for item in title_property.title)

    def _get_database_property(
        self, name: str, property_type: type[DatabasePropertyT]
    ) -> DatabasePropertyT | None:
        """Get a database property by name and type with type safety."""
        prop = self._properties.get(name)
        if isinstance(prop, property_type):
            return prop
        return None

    async def _paginate_database(
        self,
        page_size: int = 100,
        filter_conditions: dict[str, Any] | None = None,
    ) -> AsyncGenerator[list[NotionPageDto], None]:
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

            result: NotionQueryDatabaseResponse = await self.client.query_database(
                database_id=self.id, query_data=query_data
            )

            if not result or not result.results:
                return

            yield result.results

            has_more = result.has_more
            start_cursor = result.next_cursor if has_more else None
