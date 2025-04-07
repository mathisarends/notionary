from typing import Any, AsyncGenerator, Dict, List, Optional, Union, TypedDict
import re

from notionary.core.notion_client import NotionClient
from notionary.core.database.notion_database_schema import NotionDatabaseSchema
from notionary.core.database.notion_database_writer import DatabaseWritter
from notionary.core.page.notion_page_manager import NotionPageManager
from notionary.util.logging_mixin import LoggingMixin
from notionary.exceptions.page_creation_exception import PageCreationException
from notionary.util.uuid_utils import format_uuid


class PageResult(TypedDict, total=False):
    """Type definition for page operation results."""
    success: bool
    page_id: str
    url: Optional[str]
    message: Optional[str]


class NotionDatabaseManager(LoggingMixin):
    """
    High-level facade for working with Notion databases.
    Provides simplified operations for creating, reading, updating and deleting pages.
    """

    def __init__(self, database_id: str, token: Optional[str] = None):
        """
        Initialize the database facade with a database ID.

        Args:
            database_id: The ID of the Notion database
            token: Optional Notion API token (uses environment variable if not provided)
        """
        self.database_id = format_uuid(database_id) or database_id
        self._client = NotionClient(token=token)
        self._schema = NotionDatabaseSchema(self.database_id, self._client)
        self._writer = DatabaseWritter(self._client, self._schema)

    async def initialize(self) -> bool:
        """
        Initialize the database facade by loading the schema.

        Returns:
            True if initialization was successful
        """
        success = await self._schema.load()
        if not success:
            self.logger.error("Failed to load schema for database %s", self.database_id)
        return success

    async def get_database_name(self) -> Optional[str]:
        """
        Get the name of the current database.

        Returns:
            The database name or None if it couldn't be retrieved
        """
        try:
            db_details = await self._client.get(f"databases/{self.database_id}")
            if not db_details:
                self.logger.error("Failed to retrieve database %s", self.database_id)
                return None
            
            title = "Untitled"
            if "title" in db_details:
                title_parts = []
                for text_obj in db_details["title"]:
                    if "plain_text" in text_obj:
                        title_parts.append(text_obj["plain_text"])
                
                if title_parts:
                    title = "".join(title_parts)
            
            return title
        except Exception as e:
            self.logger.error("Error getting database name: %s", str(e))
            return None

    async def get_property_types(self) -> Dict[str, str]:
        """
        Get all property types for the database.

        Returns:
            Dictionary mapping property names to their types
        """
        return await self._schema.get_property_types()

    async def get_select_options(self, property_name: str) -> List[Dict[str, str]]:
        """
        Get options for a select, multi-select, or status property.

        Args:
            property_name: Name of the property

        Returns:
            List of select options with name, id, and color (if available)
        """
        options = await self._schema.get_select_options(property_name)
        return [
            {
                "name": option.get("name", ""),
                "id": option.get("id", ""),
                "color": option.get("color", "")
            }
            for option in options
        ]

    async def get_relation_options(self, property_name: str, limit: int = 100) -> List[Dict[str, str]]:
        """
        Get available options for a relation property.

        Args:
            property_name: Name of the relation property
            limit: Maximum number of options to retrieve

        Returns:
            List of relation options with id and title
        """
        options = await self._schema.get_relation_options(property_name, limit)
        return [
            {
                "id": option.get("id", ""),
                "title": option.get("title", "")
            }
            for option in options
        ]

    async def create_page(
        self,
        properties: Dict[str, Any],
        relations: Optional[Dict[str, Union[str, List[str]]]] = None
    ) -> PageResult:
        """
        Create a new page in the database.

        Args:
            properties: Dictionary of property names and values
            relations: Optional dictionary of relation property names and titles

        Returns:
            Result object with success status and page information
        """
        try:
            response = await self._writer.create_page(
                self.database_id, properties, relations
            )
            
            if not response:
                return {
                    "success": False,
                    "message": f"Failed to create page in database {self.database_id}"
                }
                
            page_id = response.get("id", "")
            page_url = response.get("url", None)
            
            return {
                "success": True,
                "page_id": page_id,
                "url": page_url
            }
                
        except PageCreationException as e:
            self.logger.warning("Page creation failed: %s", str(e))
            return {
                "success": False,
                "message": str(e)
            }

    async def update_page(
        self,
        page_id: str,
        properties: Optional[Dict[str, Any]] = None,
        relations: Optional[Dict[str, Union[str, List[str]]]] = None
    ) -> PageResult:
        """
        Update an existing page.

        Args:
            page_id: The ID of the page to update
            properties: Dictionary of property names and values to update
            relations: Optional dictionary of relation property names and titles

        Returns:
            Result object with success status and message
        """
        try:
            formatted_page_id = self._format_page_id(page_id)
            
            response = await self._writer.update_page(
                formatted_page_id, properties, relations
            )
            
            if not response:
                return {
                    "success": False,
                    "message": f"Failed to update page {formatted_page_id}"
                }
                
            return {
                "success": True,
                "page_id": formatted_page_id
            }
            
        except Exception as e:
            self.logger.error("Error updating page: %s", str(e))
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def delete_page(self, page_id: str) -> PageResult:
        """
        Delete (archive) a page.

        Args:
            page_id: The ID of the page to delete

        Returns:
            Result object with success status and message
        """
        try:
            formatted_page_id = self._format_page_id(page_id)
            
            success = await self._writer.delete_page(formatted_page_id)
            
            if not success:
                return {
                    "success": False,
                    "message": f"Failed to delete page {formatted_page_id}"
                }
                
            return {
                "success": True,
                "page_id": formatted_page_id
            }
            
        except Exception as e:
            self.logger.error("Error deleting page: %s", str(e))
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def get_pages(
        self, 
        limit: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None
    ) -> List[NotionPageManager]:
        """
        Get all pages from the database.

        Args:
            limit: Maximum number of pages to retrieve
            filter_conditions: Optional filter to apply to the database query
            sorts: Optional sort instructions for the database query

        Returns:
            List of NotionPageManager instances for each page
        """
        pages: List[NotionPageManager] = []
        count = 0
        
        async for page in self.iter_pages(
            page_size=min(limit, 100),
            filter_conditions=filter_conditions,
            sorts=sorts
        ):
            pages.append(page)
            count += 1
            
            if count >= limit:
                break
                
        return pages

    async def iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[NotionPageManager, None]:
        """
        Asynchronous generator that yields pages from the database.

        Args:
            page_size: Number of pages to fetch per request
            filter_conditions: Optional filter to apply to the database query
            sorts: Optional sort instructions for the database query

        Yields:
            NotionPageManager instances for each page
        """
        async for page_manager in self._schema.iter_database_pages(
            database_id=self.database_id,
            page_size=page_size,
            filter_conditions=filter_conditions,
            sorts=sorts
        ):
            yield page_manager

    async def get_page_manager(self, page_id: str) -> Optional[NotionPageManager]:
        """
        Get a NotionPageManager for a specific page.

        Args:
            page_id: The ID of the page

        Returns:
            NotionPageManager instance or None if the page wasn't found
        """
        formatted_page_id = self._format_page_id(page_id)
        
        try:
            page_data = await self._client.get(f"pages/{formatted_page_id}")
            
            if not page_data:
                self.logger.error("Page %s not found", formatted_page_id)
                return None
                
            # Extract title
            title = self._extract_title_from_page(page_data)
            
            # Create page manager
            return NotionPageManager(
                page_id=formatted_page_id,
                title=title,
                url=page_data.get("url")
            )
            
        except Exception as e:
            self.logger.error("Error getting page manager: %s", str(e))
            return None

    def _extract_title_from_page(self, page: Dict[str, Any]) -> str:
        """
        Extract the title from a page object.

        Args:
            page: A page object from the Notion API

        Returns:
            The extracted title or "Untitled" if no title is found
        """
        return self._schema.extract_title_from_page(page)

    def _format_page_id(self, page_id: str) -> str:
        return format_uuid(page_id) or page_id


    async def close(self) -> None:
        """Close the client connection."""
        await self._client.close()