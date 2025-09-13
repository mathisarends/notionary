from __future__ import annotations

import asyncio
import random
from typing import Any, AsyncGenerator, Dict, Optional

from notionary import NotionPage
from notionary.database.client import NotionDatabaseClient
from notionary.database.database_filter_builder import DatabaseFilterBuilder
from notionary.database.database_provider import NotionDatabaseProvider
from notionary.database.models import (
    NotionDatabaseResponse,
    NotionPageResponse,
    NotionQueryDatabaseResponse,
)
from notionary.util import LoggingMixin, factory_only


class NotionDatabase(LoggingMixin):
    """
    Minimal manager for Notion databases.
    Focused exclusively on creating basic pages and retrieving page managers
    for further page operations.
    """

    @factory_only("from_database_id", "from_database_name")
    def __init__(
        self,
        id: str,
        title: str,
        url: str,
        emoji_icon: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        token: Optional[str] = None,
    ):
        """
        Initialize the minimal database manager.
        """
        self._id = id
        self._title = title
        self._url = url
        self._emoji_icon = emoji_icon
        self._properties = properties

        self.client = NotionDatabaseClient(token=token)

    @classmethod
    async def from_database_id(
        cls, id: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabase from a database ID using NotionDatabaseProvider.
        """
        provider = cls.get_database_provider()

        return await provider.get_database_by_id(id, token)

    @classmethod
    async def from_database_name(
        cls,
        database_name: str,
        token: Optional[str] = None,
        min_similarity: float = 0.6,
    ) -> NotionDatabase:
        """
        Create a NotionDatabase by finding a database with fuzzy matching on the title using NotionDatabaseProvider.
        """
        provider = cls.get_database_provider()
        return await provider.get_database_by_name(database_name, token, min_similarity)

    @property
    def id(self) -> str:
        """Get the database ID (readonly)."""
        return self._id

    @property
    def title(self) -> str:
        """Get the database title (readonly)."""
        return self._title

    @property
    def url(self) -> str:
        """Get the database URL (readonly)."""
        return self._url

    @property
    def emoji(self) -> Optional[str]:
        """Get the database emoji (readonly)."""
        return self._emoji_icon

    @property
    def properties(self) -> Optional[Dict[str, Any]]:
        """Get the database properties (readonly)."""
        return self._properties

    # Database Provider is a singleton so we can instantiate it here with no worries
    @property
    def database_provider(self):
        """Return a NotionDatabaseProvider instance for this database."""
        return NotionDatabaseProvider.get_instance()

    @classmethod
    def get_database_provider(cls):
        """Return a NotionDatabaseProvider instance for class-level usage."""
        return NotionDatabaseProvider.get_instance()

    async def create_blank_page(self) -> NotionPage:
        """
        Create a new blank page in the database with minimal properties.
        """
        create_page_response: NotionPageResponse = await self.client.create_page(
            parent_database_id=self.id
        )

        return await NotionPage.from_page_id(page_id=create_page_response.id)

    async def set_title(self, new_title: str) -> str:
        """
        Update the database title.
        """
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
        """
        Update the database cover image.
        """
        result = await self.client.update_database_cover_image(
            database_id=self.id, image_url=image_url
        )

        if not result.cover or not result.cover.external:
            raise ValueError(f"Failed to set cover image to {image_url}")

        self.database_provider.invalidate_database_cache(database_id=self.id)
        return result.cover.external.url

    async def set_random_gradient_cover(self) -> str:
        """Sets a random gradient cover from Notion's default gradient covers."""
        default_notion_covers = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.png"
            for i in range(1, 10)
        ]
        random_cover_url = random.choice(default_notion_covers)
        return await self.set_cover_image(random_cover_url)

    async def set_external_icon(self, external_icon_url: str) -> str:
        """
        Update the database icon with an external image URL.
        """
        result = await self.client.update_database_external_icon(
            database_id=self.id, icon_url=external_icon_url
        )

        if not result.icon or not result.icon.external:
            raise ValueError(f"Failed to set external icon to {external_icon_url}")

        self.database_provider.invalidate_database_cache(database_id=self.id)
        return result.icon.external.url

    async def get_options_by_property_name(self, property_name: str) -> list[str]:
        """
        Retrieve all option names for a select, multi_select, status, or relation property.

        Args:
            property_name: The name of the property in the database schema.

        Returns:
            A list of option names for the given property. For select, multi_select, or status,
            returns the option names directly. For relation properties, returns the titles of related pages.
        """
        property_schema = self.properties.get(property_name)

        property_type = property_schema.get("type")

        if property_type in ["select", "multi_select", "status"]:
            options = property_schema.get(property_type, {}).get("options", [])
            return [option.get("name", "") for option in options]

        if property_type == "relation":
            return await self._get_relation_options(property_name)

        return []

    def get_property_type(self, property_name: str) -> Optional[str]:
        """
        Get the type of a property by its name.
        """
        property_schema = self.properties.get(property_name)
        return property_schema.get("type") if property_schema else None

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

        for page in search_results.results:
            page = await NotionPage.from_page_id(
                page_id=page.id, token=self.client.token
            )
            page_results.append(page)

        return page_results

    async def iter_pages_updated_within(
        self, hours: int = 24, page_size: int = 100
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Iterate through pages edited in the last N hours using DatabaseFilterBuilder.
        """

        filter_builder = DatabaseFilterBuilder()
        filter_builder.with_updated_last_n_hours(hours).with_page_size(page_size)
        filter_conditions = filter_builder.build()

        async for page in self._iter_pages(
            page_size=page_size, filter_conditions=filter_conditions
        ):
            yield page

    async def get_all_pages(self) -> list[NotionPage]:
        """
        Get all pages in the database (use with caution for large databases).
        Uses asyncio.gather to parallelize NotionPage creation per API page.
        """
        pages: list[NotionPage] = []
        start_cursor: Optional[str] = None
        has_more = True
        body: Dict[str, Any] = {"page_size": 100}

        while has_more:
            current_body = body.copy()
            if start_cursor:
                current_body["start_cursor"] = start_cursor

            result = await self.client.query_database(
                database_id=self.id, query_data=current_body
            )

            if not result or not result.results:
                break

            # Parallelize NotionPage creation for this batch
            page_tasks = [
                NotionPage.from_page_id(page_id=page.id, token=self.client.token)
                for page in result.results
            ]
            batch_pages = await asyncio.gather(*page_tasks)
            pages.extend(batch_pages)

            has_more = result.has_more
            start_cursor = result.next_cursor if has_more else None

        return pages

    async def get_last_edited_time(self) -> str:
        """
        Retrieve the last edited time of the database.

        Returns:
            ISO 8601 timestamp string of the last database edit.
        """
        db = await self.client.get_database(self.id)
        return db.last_edited_time

    def create_filter(self) -> DatabaseFilterBuilder:
        """Create a new filter builder for this database."""
        return DatabaseFilterBuilder()

    async def iter_pages_with_filter(
        self, filter_builder: DatabaseFilterBuilder, page_size: int = 100
    ):
        """Iterate pages using a filter builder."""
        filter_config = filter_builder.build()
        async for page in self._iter_pages(
            page_size=page_size, filter_conditions=filter_config
        ):
            yield page

    async def _iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Asynchronous generator that yields pages from the database.
        Directly queries the Notion API without using the schema.
        """
        start_cursor: Optional[str] = None
        has_more = True

        body: Dict[str, Any] = {"page_size": page_size}

        if filter_conditions:
            body["filter"] = filter_conditions

        while has_more:
            current_body = body.copy()
            if start_cursor:
                current_body["start_cursor"] = start_cursor

            result = await self.client.query_database(
                database_id=self.id, query_data=current_body
            )

            if not result or not result.results:
                return

            for page in result.results:
                yield await NotionPage.from_page_id(
                    page_id=page.id, token=self.client.token
                )

            has_more = result.has_more
            start_cursor = result.next_cursor if has_more else None

    @classmethod
    def _create_from_response(
        cls, db_response: NotionDatabaseResponse, token: Optional[str]
    ) -> NotionDatabase:
        """
        Create NotionDatabase instance from API response.
        """
        title = cls._extract_title(db_response)
        emoji_icon = cls._extract_emoji_icon(db_response)

        return cls(
            id=db_response.id,
            title=title,
            url=db_response.url,
            emoji_icon=emoji_icon,
            properties=db_response.properties,
            token=token,
        )

    @staticmethod
    def _extract_title(db_response: NotionDatabaseResponse) -> str:
        """Extract title from database response."""
        if db_response.title and len(db_response.title) > 0:
            return db_response.title[0].plain_text
        return "Untitled Database"

    @staticmethod
    def _extract_emoji_icon(db_response: NotionDatabaseResponse) -> Optional[str]:
        """Extract emoji from database response."""
        if not db_response.icon:
            return None

        if db_response.icon.type == "emoji":
            return db_response.icon.emoji

        return None

    def _extract_title_from_page(self, page: NotionPageResponse) -> Optional[str]:
        """
        Extracts the title from a NotionPageResponse object.
        """
        if not page.properties:
            return None

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

    async def _get_relation_options(self, property_name: str) -> list[str]:
        """
        Retrieve the titles of all pages related to a relation property.

        Args:
            property_name: The name of the relation property in the database schema.

        Returns:
            A list of titles for all related pages. Returns an empty list if no related pages are found.
        """
        property_schema = self.properties.get(property_name)

        relation_database_id = property_schema.get("relation", {}).get("database_id")

        search_results = await self.client.query_database(
            database_id=relation_database_id
        )

        return [self._extract_title_from_page(page) for page in search_results.results]
