from __future__ import annotations

import asyncio
import random
from typing import Any, AsyncGenerator, Optional

from notionary.database.client import NotionDatabaseClient
from notionary.database.database_filter_builder import DatabaseFilterBuilder
from notionary.database.database_provider import NotionDatabaseProvider
from notionary.database.models import (
    NotionDatabaseResponse,
    NotionQueryDatabaseResponse,
)
from notionary.page.page_models import NotionPageDto
from notionary.page.notion_page import NotionPage
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
        properties: Optional[dict[str, Any]] = None,
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
    def properties(self) -> Optional[dict[str, Any]]:
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

    async def create_blank_page(self) -> Optional[NotionPage]:
        """
        Create a new blank page in the database with minimal properties.
        """
        try:
            create_page_response: NotionPageDto = await self.client.create_page(
                parent_database_id=self.id
            )

            return await NotionPage.from_page_id(page_id=create_page_response.id)

        except Exception as e:
            self.logger.error("Error creating blank page: %s", str(e))
            return None

    async def set_title(self, new_title: str) -> bool:
        """
        Update the database title.
        """
        try:
            result = await self.client.update_database_title(
                database_id=self.id, title=new_title
            )

            self._title = result.title[0].plain_text
            self.logger.info(f"Successfully updated database title to: {new_title}")
            self.database_provider.invalidate_database_cache(database_id=self.id)
            return True

        except Exception as e:
            self.logger.error(f"Error updating database title: {str(e)}")
            return False

    async def set_emoji(self, new_emoji: str) -> bool:
        """
        Update the database emoji.
        """
        try:
            result = await self.client.update_database_emoji(
                database_id=self.id, emoji=new_emoji
            )

            self._emoji_icon = result.icon.emoji if result.icon else None
            self.logger.info(f"Successfully updated database emoji to: {new_emoji}")
            self.database_provider.invalidate_database_cache(database_id=self.id)
            return True

        except Exception as e:
            self.logger.error(f"Error updating database emoji: {str(e)}")
            return False

    async def set_cover_image(self, image_url: str) -> Optional[str]:
        """
        Update the database cover image.
        """
        try:
            result = await self.client.update_database_cover_image(
                database_id=self.id, image_url=image_url
            )

            if result.cover and result.cover.external:
                self.database_provider.invalidate_database_cache(database_id=self.id)
                return result.cover.external.url
            return None

        except Exception as e:
            self.logger.error(f"Error updating database cover image: {str(e)}")
            return None

    async def set_random_gradient_cover(self) -> Optional[str]:
        """Sets a random gradient cover from Notion's default gradient covers (always jpg)."""
        default_notion_covers = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.png"
            for i in range(1, 10)
        ]
        random_cover_url = random.choice(default_notion_covers)
        return await self.set_cover_image(random_cover_url)

    async def set_external_icon(self, external_icon_url: str) -> Optional[str]:
        """
        Update the database icon with an external image URL.
        """
        try:
            result = await self.client.update_database_external_icon(
                database_id=self.id, icon_url=external_icon_url
            )

            if result.icon and result.icon.external:
                self.database_provider.invalidate_database_cache(database_id=self.id)
                return result.icon.external.url
            return None

        except Exception as e:
            self.logger.error(f"Error updating database external icon: {str(e)}")
            return None

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
            # Parallelize NotionPage creation for this batch
            page_tasks = [
                NotionPage.from_page_id(
                    page_id=page_response.id, token=self.client.token
                )
                for page_response in batch
            ]
            batch_pages = await asyncio.gather(*page_tasks)
            pages.extend(batch_pages)

        return pages

    async def get_last_edited_time(self) -> Optional[str]:
        """
        Retrieve the last edited time of the database.

        Returns:
            ISO 8601 timestamp string of the last database edit, or None if request fails.
        """
        try:
            db = await self.client.get_database(self.id)

            return db.last_edited_time

        except Exception as e:
            self.logger.error(
                "Error fetching last_edited_time for database %s: %s",
                self.id,
                str(e),
            )
            return None

    async def _iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Asynchronous generator that yields NotionPage objects from the database.
        Directly queries the Notion API without using the schema.

        Args:
            page_size: Number of pages to fetch per request
            filter_conditions: Optional filter conditions

        Yields:
            NotionPage objects
        """
        self.logger.debug(
            "Iterating pages with page_size: %d, filter: %s",
            page_size,
            filter_conditions,
        )

        async for batch in self._paginate_database(page_size, filter_conditions):
            for page_response in batch:
                yield await NotionPage.from_page_id(
                    page_id=page_response.id, token=self.client.token
                )

    @classmethod
    def _create_from_response(
        cls, db_response: NotionDatabaseResponse, token: Optional[str]
    ) -> NotionDatabase:
        """
        Create NotionDatabase instance from API response.
        """
        title = cls._extract_title(db_response)
        emoji_icon = cls._extract_emoji_icon(db_response)

        instance = cls(
            id=db_response.id,
            title=title,
            url=db_response.url,
            emoji_icon=emoji_icon,
            properties=db_response.properties,
            token=token,
        )

        cls.logger.info(
            "Created database manager: '%s' (ID: %s)", title, db_response.id
        )

        return instance

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

    def _extract_title_from_page(self, page: NotionPageDto) -> Optional[str]:
        """
        Extracts the title from a NotionPageDto object.
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

    async def _get_relation_options(self, property_name: str) -> list[dict[str, Any]]:
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

    async def _paginate_database(
        self,
        page_size: int = 100,
        filter_conditions: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[list[NotionPageDto], None]:
        """
        Central pagination logic for Notion Database queries.

        Args:
            page_size: Number of pages per request (max 100)
            filter_conditions: Optional filter conditions for the query

        Yields:
            Batches of NotionPageDto objects
        """
        start_cursor: Optional[str] = None
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
