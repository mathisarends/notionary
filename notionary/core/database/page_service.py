from typing import Dict, Optional, Any, List, Union, TYPE_CHECKING
from notionary.core.database.models.page_result import PageResult
from notionary.core.database.notion_database_schema import NotionDatabaseSchema
from notionary.core.database.notion_database_writer import DatabaseWritter
from notionary.core.notion_client import NotionClient

from notionary.core.page.notion_page_manager import NotionPageManager
from notionary.exceptions.database_exceptions import (
    PageNotFoundException,
    PageOperationError,
)
from notionary.exceptions.page_creation_exception import PageCreationException
from notionary.util.uuid_utils import format_uuid


class DatabasePageService:
    """Service für den Umgang mit Datenbankseiten"""

    def __init__(
        self,
        client: NotionClient,
        schema: NotionDatabaseSchema,
        writer: DatabaseWritter,
    ):
        self._client = client
        self._schema = schema
        self._writer = writer

    def _format_page_id(self, page_id: str) -> str:
        """
        Format a page ID to ensure it's in the correct format.

        Args:
            page_id: The page ID to format

        Returns:
            The formatted page ID
        """
        return format_uuid(page_id) or page_id

    async def create_page(
        self,
        database_id: str,
        properties: Dict[str, Any],
        relations: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> PageResult:
        """
        Create a new page in the database.

        Args:
            database_id: The database ID to create the page in
            properties: Dictionary of property names and values
            relations: Optional dictionary of relation property names and titles

        Returns:
            Result object with success status and page information
        """
        try:
            response = await self._writer.create_page(
                database_id, properties, relations
            )

            if not response:
                return {
                    "success": False,
                    "message": f"Failed to create page in database {database_id}",
                }

            page_id = response.get("id", "")
            page_url = response.get("url", None)

            return {"success": True, "page_id": page_id, "url": page_url}

        except PageCreationException as e:
            return {"success": False, "message": str(e)}

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
        try:
            formatted_page_id = self._format_page_id(page_id)

            response = await self._writer.update_page(
                formatted_page_id, properties, relations
            )

            if not response:
                return {
                    "success": False,
                    "message": f"Failed to update page {formatted_page_id}",
                }

            return {"success": True, "page_id": formatted_page_id}

        except PageOperationError as e:
            return {"success": False, "message": f"Error: {str(e)}"}

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
                    "message": f"Failed to delete page {formatted_page_id}",
                }

            return {"success": True, "page_id": formatted_page_id}

        except PageOperationError as e:
            return {"success": False, "message": f"Error: {str(e)}"}

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
                return None

            return NotionPageManager(
                page_id=formatted_page_id, url=page_data.get("url")
            )

        except PageNotFoundException:
            return None
