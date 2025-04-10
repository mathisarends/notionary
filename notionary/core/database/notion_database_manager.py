from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from notionary.core.database.database_info_service import DatabaseInfoService
from notionary.core.database.database_query_service import DatabaseQueryService
from notionary.core.database.database_schema_service import DatabaseSchemaService
from notionary.core.database.models.page_result import PageResult
from notionary.core.database.page_service import DatabasePageService
from notionary.core.notion_client import NotionClient
from notionary.core.database.notion_database_schema import NotionDatabaseSchema
from notionary.core.database.notion_database_writer import DatabaseWritter
from notionary.core.page.notion_page_manager import NotionPageManager
from notionary.exceptions.database_exceptions import (
    DatabaseInitializationError,
    PropertyError,
)
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import format_uuid


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

        self._info_service = DatabaseInfoService(self._client, self.database_id)
        self._page_service = DatabasePageService(
            self._client, self._schema, self._writer
        )
        self._query_service = DatabaseQueryService(self._schema)
        self._schema_service = DatabaseSchemaService(self._schema)

    @property
    def title(self) -> Optional[str]:
        """Get the database title."""
        return self._info_service.title

    async def initialize(self) -> bool:
        """
        Initialize the database facade by loading the schema.

        This method needs to be called after creating a new instance via the constructor.
        When using NotionDatabaseFactory, this is called automatically.
        """
        try:
            success = await self._schema.load()
            if not success:
                self.logger.error(
                    "Failed to load schema for database %s", self.database_id
                )
                return False

            await self._info_service.load_title()
            self.logger.debug("Loaded database title: %s", self.title)

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
                "Database manager not initialized. Call initialize() first.",
            )

    async def get_database_name(self) -> Optional[str]:
        """
        Get the name of the current database.

        Returns:
            The database name or None if it couldn't be retrieved
        """
        await self._ensure_initialized()

        if self.title:
            return self.title

        try:
            return await self._info_service.load_title()
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
        return await self._schema_service.get_property_types()

    async def get_select_options(self, property_name: str) -> List[Dict[str, str]]:
        """
        Get options for a select, multi-select, or status property.

        Args:
            property_name: Name of the property

        Returns:
            List of select options with name, id, and color (if available)
        """
        await self._ensure_initialized()
        return await self._schema_service.get_select_options(property_name)

    async def get_relation_options(
        self, property_name: str, limit: int = 100
    ) -> List[Dict[str, str]]:
        """
        Get available options for a relation property.

        Args:
            property_name: Name of the relation property
            limit: Maximum number of options to retrieve

        Returns:
            List of relation options with id and title
        """
        await self._ensure_initialized()
        return await self._schema_service.get_relation_options(property_name, limit)

    async def create_page(
        self,
        properties: Dict[str, Any],
        relations: Optional[Dict[str, Union[str, List[str]]]] = None,
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

        result = await self._page_service.create_page(
            self.database_id, properties, relations
        )

        if result["success"]:
            self.logger.info(
                "Created page %s in database %s",
                result.get("page_id", ""),
                self.database_id,
            )
        else:
            self.logger.warning("Page creation failed: %s", result.get("message", ""))

        return result

    async def update_page(
        self,
        page_id: str,
        properties: Optional[Dict[str, Any]] = None,
        relations: Optional[Dict[str, Union[str, List[str]]]] = None,
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

        self.logger.debug("Updating page %s", page_id)

        result = await self._page_service.update_page(page_id, properties, relations)

        if result["success"]:
            self.logger.info("Successfully updated page %s", result.get("page_id", ""))
        else:
            self.logger.error(
                "Error updating page %s: %s", page_id, result.get("message", "")
            )

        return result

    async def delete_page(self, page_id: str) -> PageResult:
        """
        Delete (archive) a page.

        Args:
            page_id: The ID of the page to delete

        Returns:
            Result object with success status and message
        """
        await self._ensure_initialized()

        self.logger.debug("Deleting page %s", page_id)

        result = await self._page_service.delete_page(page_id)

        if result["success"]:
            self.logger.info("Successfully deleted page %s", result.get("page_id", ""))
        else:
            self.logger.error(
                "Error deleting page %s: %s", page_id, result.get("message", "")
            )

        return result

    async def get_pages(
        self,
        limit: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
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
            sorts,
        )

        pages = await self._query_service.get_pages(
            self.database_id, limit, filter_conditions, sorts
        )

        self.logger.debug(
            "Retrieved %d pages from database %s", len(pages), self.database_id
        )
        return pages

    async def iter_pages(
        self,
        page_size: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
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
            sorts,
        )

        async for page_manager in self._query_service.iter_pages(
            self.database_id, page_size, filter_conditions, sorts
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

        self.logger.debug("Getting page manager for page %s", page_id)

        page_manager = await self._page_service.get_page_manager(page_id)

        if not page_manager:
            self.logger.error("Page %s not found", page_id)

        return page_manager

    async def close(self) -> None:
        """Close the client connection."""
        await self._client.close()


    # TODO: Idee wäre hier noch ein Enum einzuführen, bin mir hier aber nicht sicher wieviel Overhead das ist.
    async def collect_database_metadata(
        self,
        include_types: Optional[List[str]] = None,
        relation_limit: int = 100
    ) -> Dict[str, Any]:
        """
        Collects all metadata of a Notion database in a structured format.
        
        This function builds a comprehensive representation of the database schema,
        including available options for select fields, status fields, and relations.
        The resulting structure is particularly useful for providing AI agents with
        context about your Notion database schema when generating prompts or
        analyzing data.
        
        Args:
            include_types: List of property types to include (e.g., ["select", "relation"]).
                        If None, all property types will be included.
            relation_limit: Maximum number of relation options to fetch per relation field.
        
        Returns:
            A structured dictionary containing database metadata and property options.
        """
        db_name = await self.get_database_name()
        property_types = await self.get_property_types()
        
        schema_metadata = {
            "database_name": db_name,
            "properties": {}
        }
        
        for prop_name, prop_type in property_types.items():
            # Skip if we're filtering property types and this one isn't included
            if include_types is not None and prop_type not in include_types:
                continue
                
            property_info = {
                "type": prop_type,
                "options": []
            }
            
            if prop_type in ["select", "multi_select", "status"]:
                options = await self.get_select_options(prop_name)
                property_info["options"] = options
            
            elif prop_type == "relation":
                relation_options = await self.get_relation_options(prop_name, limit=relation_limit)
                property_info["options"] = relation_options
            
            schema_metadata["properties"][prop_name] = property_info
        
        return schema_metadata