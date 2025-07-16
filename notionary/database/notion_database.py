from __future__ import annotations
import random
from typing import Any, AsyncGenerator, Dict, List, Optional

from notionary.models.notion_database_response import (
    NotionDatabaseResponse,
    NotionPageResponse,
    NotionQueryDatabaseResponse,
)
from notionary.models.notion_page_response import EmojiIcon
from notionary.notion_client import NotionClient
from notionary.page.notion_page import NotionPage
from notionary.util import LoggingMixin
from notionary.util.page_id_utils import format_uuid
from notionary.exceptions.database_exceptions import (
    DatabaseConnectionError,
    DatabaseNotFoundException,
)

from notionary.common.filter_builder import FilterBuilder


class NotionDatabase(LoggingMixin):
    """
    Minimal manager for Notion databases.
    Focused exclusively on creating basic pages and retrieving page managers
    for further page operations.
    """

    def __init__(self, database_id: str, title: str, url: str, emoji: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize the minimal database manager.
        """
        self._database_id = database_id
        self._title = title
        self._url = url
        self._emoji = emoji
        
        self._client = NotionClient(token=token)
        
    @classmethod
    async def from_database_id(
        cls, database_id: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabase from a database ID.
        """
        formatted_id = format_uuid(database_id) or database_id
        
        temp_client = NotionClient(token=token)
        
        try:
            db = await temp_client.get_database(formatted_id)
            title = db.title[0].plain_text
            url = db.url
            
            emoji = db.icon.emoji if db.icon.type == "emoji" else None
            
            emoji = db.icon.type == "emoji" if db.icon else None
            
            instance = cls(formatted_id, title, url=url, emoji=emoji, token=token)

            cls.logger.info(
                "Successfully created database manager for ID: %s (Title: '%s', URL: '%s')", 
                formatted_id, title, url
            )
            return instance
            
        except Exception as e:
            error_msg = f"Error fetching database info for ID {formatted_id}: {str(e)}"
            cls.logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e

    @classmethod
    async def from_database_name(
        cls, database_name: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabase by finding a database with a matching name.
        Uses Notion's search API and takes the first (best) result.
        """
        from notionary.workspace.workspace import NotionWorkspace

        cls.logger.debug("Searching for database with name: %s", database_name)
        workspace = NotionWorkspace()

        try:
            cls.logger.debug("Using search endpoint to find databases")

            databases = await workspace.search_databases(database_name, limit=1)

            if not databases:
                cls.logger.warning("No databases found for name: %s", database_name)
                raise DatabaseNotFoundException(database_name)

            # Take the first result - Notion's search already ranks by relevance
            matched_db = databases[0]
            database_id = matched_db.database_id
            
            # Query the database to get current title, url and emoji
            temp_client = NotionClient(token=token)
            db = await temp_client.get_database(database_id)
            title = db.title[0].plain_text if db.title else "Untitled Database"
            url = db.url
            emoji = getattr(db.icon, "emoji", None) if db.icon and isinstance(db.icon, EmojiIcon) else None

            cls.logger.info(
                "Found matching database: '%s' (ID: %s, URL: '%s')",
                title,
                database_id,
                url
            )

            manager = cls(database_id, title, url=url, emoji=emoji, token=token)

            cls.logger.info(
                "Successfully created database manager for '%s'", title
            )
            return manager
            
        except Exception as e:
            error_msg = f"Error finding database by name: {str(e)}"
            cls.logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e
        
    @property
    def database_id(self) -> str:
        """Get the database ID (readonly)."""
        return self._database_id

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
        return self._emoji

    async def create_blank_page(self) -> Optional[NotionPage]:
        """
        Create a new blank page in the database with minimal properties.
        """
        try:
            create_page_response: NotionPageResponse = await self._client.create_page(
                parent_database_id=self.database_id
            )

            return NotionPage.from_page_id(page_id=create_page_response.id)

        except Exception as e:
            self.logger.error("Error creating blank page: %s", str(e))
            return None

    async def archive_page(self, page_id: str) -> bool:
        """
        Delete (archive) a page.
        """
        try:
            formatted_page_id = format_uuid(page_id)

            result = await self._client.patch_page(
                formatted_page_id, {"archived": True}
            )

            if not result:
                self.logger.error("Error deleting page %s", formatted_page_id)
                return False

            self.logger.info(
                "Page %s successfully deleted (archived)", formatted_page_id
            )
            return True

        except Exception as e:
            self.logger.error("Error in archive_page: %s", str(e))
            return False
        
    async def set_title(self, new_title: str) -> bool:
        """
        Update the database title.
        """
        try:
            update_data = {
                "title": [
                    {
                        "text": {
                            "content": new_title
                        }
                    }
                ]
            }
            
            result = await self._client.patch_database(
                database_id=self.database_id, 
                data=update_data
            )
            
            self._title = result.title[0].plain_text
            
            self.logger.info(f"Successfully updated database title to: {new_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating database title: {str(e)}")
            return False
        
    async def set_emoji(self, new_emoji: str) -> bool:
        """
        Update the database emoji.
        """
        try:
            icon = {"type": "emoji", "emoji": new_emoji}
            
            result = await self._client.patch_database(
                database_id=self.database_id, 
                data={"icon": icon}
            )
            
            self._emoji = result.icon.emoji if result.icon else None
            
            self.logger.info(f"Successfully updated database emoji to: {new_emoji}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating database emoji: {str(e)}")
            return False
        
    async def set_cover_image(self, image_url: str) -> Optional[str]:
        """
        Update the database cover image.
        """
        try:
            data = {"cover": {"type": "external", "external": {"url": image_url}}}
            
            result = await self._client.patch_database(
                database_id=self.database_id, 
                data=data
            )
            return result.cover.external.url
            
        except Exception as e:
            self.logger.error(f"Error updating database cover image: {str(e)}")
            return None
        
    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        """Sets a random gradient cover from Notion's default gradient covers."""
        default_notion_covers = [
            f"https://www.notion.so/images/page-cover/gradients_{i}.{'jpg' if i in (10, 11) else 'png'}"
            for i in range(1, 12)
        ]
        random_cover_url = random.choice(default_notion_covers)
        return await self.set_cover_image(random_cover_url)
        
    async def set_external_icon(self, external_icon_url: str) -> Optional[str]:
        try:
            icon = {"type": "external", "external": {"url": external_icon_url}}
            result = await self._client.patch_database(
                database_id=self.database_id, data={"icon": icon}
            )
            
            return result.icon.external.url
        
        except Exception as e:
            self.logger.error(f"Error updating database emoji: {str(e)}")

    async def query_database_by_title(self, page_title: str) -> List[NotionPage]:
        """
        Query the database for pages with a specific title.
        """
        search_results: NotionQueryDatabaseResponse = (
            await self._client.query_database_by_title(
                database_id=self.database_id, page_title=page_title
            )
        )

        page_results: List[NotionPage] = []

        for page in search_results.results:
            page = NotionPage.from_page_id(page_id=page.id, token=self._client.token)
            page_results.append(page)

        return page_results

    async def iter_pages_updated_within(
        self, hours: int = 24, page_size: int = 100
    ) -> AsyncGenerator[NotionPage, None]:
        """
        Iterate through pages edited in the last N hours using FilterBuilder.
        """

        filter_builder = FilterBuilder()
        filter_builder.with_updated_last_n_hours(hours).with_page_size(page_size)
        filter_conditions = filter_builder.build()

        async for page in self._iter_pages(
            page_size=page_size, filter_conditions=filter_conditions
        ):
            yield page

    async def get_all_pages(self) -> List[NotionPage]:
        """
        Get all pages in the database (use with caution for large databases).
        """
        pages = []
        async for page in self._iter_pages():
            pages.append(page)
        return pages

    async def get_last_edited_time(self) -> Optional[str]:
        """
        Retrieve the last edited time of the database.

        Returns:
            ISO 8601 timestamp string of the last database edit, or None if request fails.
        """
        try:
            db = await self._client.get_database(self.database_id)

            return db.last_edited_time

        except Exception as e:
            self.logger.error(
                "Error fetching last_edited_time for database %s: %s",
                self.database_id,
                str(e),
            )
            return None


    def create_filter(self) -> FilterBuilder:
        """Create a new filter builder for this database."""
        return FilterBuilder()

    async def iter_pages_with_filter(
        self, filter_builder: FilterBuilder, page_size: int = 100
    ):
        """Iterate pages using a filter builder."""
        filter_config = filter_builder.build()
        self.logger.debug("Using filter: %s", filter_config)
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
        self.logger.debug(
            "Iterating pages with page_size: %d, filter: %s",
            page_size,
            filter_conditions,
        )

        start_cursor: Optional[str] = None
        has_more = True

        body: Dict[str, Any] = {"page_size": page_size}

        if filter_conditions:
            body["filter"] = filter_conditions

        while has_more:
            current_body = body.copy()
            if start_cursor:
                current_body["start_cursor"] = start_cursor

            result = await self._client.query_database(
                database_id=self.database_id, query_data=current_body
            )

            if not result or not result.results:
                return

            for page in result.results:
                yield NotionPage.from_page_id(page_id=page.id, token=self._client.token)

            has_more = result.has_more
            start_cursor = result.next_cursor if has_more else None