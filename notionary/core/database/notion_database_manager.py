from typing import Any, AsyncGenerator, Dict, List, Optional, Union, TypedDict

from notionary.core.notion_client import NotionClient
from notionary.core.database.notion_database_schema import NotionDatabaseSchema
from notionary.core.database.notion_database_writer import DatabaseWritter
from notionary.core.page.notion_page_manager import NotionPageManager
from notionary.exceptions.database_exceptions import DatabaseInitializationError, PageNotFoundException, PageOperationError, PropertyError
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
    
    Note:
        It is recommended to create instances of this class using the NotionDatabaseFactory
        instead of directly calling the constructor.
    """

    def __init__(self, database_id: str, token: Optional[str] = None):
        """
        Initialize the database facade with a database ID.
        
        Note:
            It's recommended to use NotionDatabaseFactory to create instances of this class
            rather than using this constructor directly.

        Args:
            database_id: The ID of the Notion database
            token: Optional Notion API token (uses environment variable if not provided)
        """
        self.database_id = format_uuid(database_id) or database_id
        self._client = NotionClient(token=token)
        self._schema = NotionDatabaseSchema(self.database_id, self._client)
        self._writer = DatabaseWritter(self._client, self._schema)
        self._initialized = False
        
        # Gets loaded in initialize()
        self._title = None
        
    @property
    def title(self) -> Optional[str]:
        """
        Get the database title.
        
        Returns:
            The database title or None if not initialized or loaded yet
        """
        return self._title
        
    async def initialize(self) -> bool:
        """
        Initialize the database facade by loading the schema.
        
        This method needs to be called after creating a new instance via the constructor.
        When using NotionDatabaseFactory, this is called automatically.
        """
        try:
            success = await self._schema.load()
            if not success:
                self.logger.error("Failed to load schema for database %s", self.database_id)
                return False
            
            # Lade den Datenbanktitel beim Initialisieren
            try:
                self._title = await self._fetch_database_title()
                self.logger.debug("Loaded database title: %s", self._title)
            except Exception as e:
                self.logger.warning("Could not load database title: %s", str(e))
                
            self._initialized = True
            return True
        except Exception as e:
            self.logger.error("Error initializing database: %s", str(e))
            return False

    async def _ensure_initialized(self) -> None:
        """
        Ensure the database manager is initialized before use.
        
        Raises:
            DatabaseInitializationError: If the database isn't initialized
        """
        if not self._initialized:
            raise DatabaseInitializationError(
                self.database_id, 
                "Database manager not initialized. Call initialize() first."
            )

    async def _fetch_database_title(self) -> str:
        """
        Fetch the database title from the Notion API.
        
        Returns:
            The database title or "Untitled" if no title is found
        """
        db_details = await self._client.get(f"databases/{self.database_id}")
        if not db_details:
            self.logger.error("Failed to retrieve database %s", self.database_id)
            return "Untitled"
        
        title = "Untitled"
        if "title" in db_details:
            title_parts = []
            for text_obj in db_details["title"]:
                if "plain_text" in text_obj:
                    title_parts.append(text_obj["plain_text"])
            
            if title_parts:
                title = "".join(title_parts)
        
        return title

    async def get_database_name(self) -> Optional[str]:
        """
        Get the name of the current database.

        Returns:
            The database name or None if it couldn't be retrieved
        """
        await self._ensure_initialized()
        
        if self._title:
            return self._title
            
        try:
            self._title = await self._fetch_database_title()
            return self._title
        except PropertyError as e:
            self.logger.error("Error getting database name: %s", str(e))
            return None
            
    async def get_property_types(self) -> Dict[str, str]:
        """
        Get all property types for the database.

        Returns:
            Dictionary mapping property names to their types
        """
        await self._ensure_initialized()
        return await self._schema.get_property_types()

    async def get_select_options(self, property_name: str) -> List[Dict[str, str]]:
        """
        Get options for a select, multi-select, or status property.

        Args:
            property_name: Name of the property

        Returns:
            List of select options with name, id, and color (if available)
        """
        await self._ensure_initialized()
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
        await self._ensure_initialized()
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
        await self._ensure_initialized()
        
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
            
            self.logger.info("Created page %s in database %s", page_id, self.database_id)
            
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
        await self._ensure_initialized()
        
        try:
            formatted_page_id = self._format_page_id(page_id)
            
            self.logger.debug("Updating page %s", formatted_page_id)
            
            response = await self._writer.update_page(
                formatted_page_id, properties, relations
            )
            
            if not response:
                self.logger.error("Failed to update page %s", formatted_page_id)
                return {
                    "success": False,
                    "message": f"Failed to update page {formatted_page_id}"
                }
                
            self.logger.info("Successfully updated page %s", formatted_page_id)
            return {
                "success": True,
                "page_id": formatted_page_id
            }
            
        except PageOperationError as e:
            self.logger.error("Error updating page %s: %s", page_id, str(e))
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
        await self._ensure_initialized()
        
        try:
            formatted_page_id = self._format_page_id(page_id)
            
            self.logger.debug("Deleting page %s", formatted_page_id)
            
            success = await self._writer.delete_page(formatted_page_id)
            
            if not success:
                self.logger.error("Failed to delete page %s", formatted_page_id)
                return {
                    "success": False,
                    "message": f"Failed to delete page {formatted_page_id}"
                }
                
            self.logger.info("Successfully deleted page %s", formatted_page_id)
            return {
                "success": True,
                "page_id": formatted_page_id
            }
            
        except PageOperationError as e:
            self.logger.error("Error deleting page %s: %s", page_id, str(e))
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
        await self._ensure_initialized()
        
        self.logger.debug(
            "Getting up to %d pages with filter: %s, sorts: %s", 
            limit, 
            filter_conditions, 
            sorts
        )
        
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
                
        self.logger.debug("Retrieved %d pages from database %s", count, self.database_id)
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
        await self._ensure_initialized()
        
        self.logger.debug(
            "Iterating pages with page_size: %d, filter: %s, sorts: %s", 
            page_size, 
            filter_conditions, 
            sorts
        )
        
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
        await self._ensure_initialized()
        
        formatted_page_id = self._format_page_id(page_id)
        
        self.logger.debug("Getting page manager for page %s", formatted_page_id)
        
        try:
            page_data = await self._client.get(f"pages/{formatted_page_id}")
            
            if not page_data:
                self.logger.error("Page %s not found", formatted_page_id)
                return None
            
            return NotionPageManager(
                page_id=formatted_page_id,
                url=page_data.get("url")
            )
            
        except PageNotFoundException as e:
            self.logger.error("Error getting page manager for %s: %s", page_id, str(e))
            return None

    def _format_page_id(self, page_id: str) -> str:
        """
        Format a page ID to ensure it's in the correct format.
        
        Args:
            page_id: The page ID to format
            
        Returns:
            The formatted page ID
        """
        return format_uuid(page_id) or page_id

    async def close(self) -> None:
        """Close the client connection."""
        await self._client.close()