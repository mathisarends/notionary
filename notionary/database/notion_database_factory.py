import logging
from typing import List, Optional, Dict, Any
from difflib import SequenceMatcher

from notionary.database.notion_database import NotionDatabase
from notionary.notion_client import NotionClient
from notionary.exceptions.database_exceptions import (
    DatabaseConnectionError,
    DatabaseInitializationError,
    DatabaseNotFoundException,
    DatabaseParsingError,
    NotionDatabaseException,
)
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import format_uuid


class NotionDatabaseFactory(LoggingMixin):
    """
    Factory class for creating NotionDatabaseManager instances.
    Provides methods for creating managers by database ID or name.
    """

    @classmethod
    async def from_database_id(
        cls, database_id: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabaseManager from a database ID.

        Args:
            database_id: The ID of the Notion database
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionDatabaseManager instance
        """
        try:
            formatted_id = format_uuid(database_id) or database_id

            manager = NotionDatabase(formatted_id, token)

            cls.logger.info(
                "Successfully created database manager for ID: %s", formatted_id
            )
            return manager

        except DatabaseInitializationError:
            raise
        except NotionDatabaseException:
            raise
        except Exception as e:
            error_msg = f"Error connecting to database {database_id}: {str(e)}"
            cls.logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e

    @classmethod
    async def from_database_name(
        cls, database_name: str, token: Optional[str] = None
    ) -> NotionDatabase:
        """
        Create a NotionDatabaseManager by finding a database with a matching name.
        Uses fuzzy matching to find the closest match to the given name.

        Args:
            database_name: The name of the Notion database to search for
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionDatabaseManager instance
        """
        cls.logger.debug("Searching for database with name: %s", database_name)

        client = NotionClient(token=token)

        try:
            cls.logger.debug("Using search endpoint to find databases")

            search_payload = {
                "filter": {"property": "object", "value": "database"},
                "page_size": 100,
            }

            response = await client.post("search", search_payload)

            if not response or "results" not in response:
                error_msg = "Failed to fetch databases using search endpoint"
                cls.logger.error(error_msg)
                raise DatabaseConnectionError(error_msg)

            databases = response.get("results", [])

            if not databases:
                error_msg = "No databases found"
                cls.logger.warning(error_msg)
                raise DatabaseNotFoundException(database_name, error_msg)

            cls.logger.debug("Found %d databases, searching for best match", len(databases))

            best_match = None
            best_score = 0

            for db in databases:
                title = cls._extract_title_from_database(db)

                score = SequenceMatcher(
                    None, database_name.lower(), title.lower()
                ).ratio()

                if score > best_score:
                    best_score = score
                    best_match = db

            if best_score < 0.6 or not best_match:
                error_msg = f"No good database name match found for '{database_name}'. Best match had score {best_score:.2f}"
                cls.logger.warning(error_msg)
                raise DatabaseNotFoundException(database_name, error_msg)

            database_id = best_match.get("id")

            if not database_id:
                error_msg = "Best match database has no ID"
                cls.logger.error(error_msg)
                raise DatabaseParsingError(error_msg)

            matched_name = cls._extract_title_from_database(best_match)

            cls.logger.info(
                "Found matching database: '%s' (ID: %s) with score: %.2f",
                matched_name,
                database_id,
                best_score,
            )

            manager = NotionDatabase(database_id, token)

            cls.logger.info("Successfully created database manager for '%s'", matched_name)
            await client.close()
            return manager

        except NotionDatabaseException:
            await client.close()
            raise
        except Exception as e:
            error_msg = f"Error finding database by name: {str(e)}"
            cls.logger.error(error_msg)
            await client.close()
            raise DatabaseConnectionError(error_msg) from e

    @classmethod
    def _extract_title_from_database(cls, database: Dict[str, Any]) -> str:
        """
        Extract the title from a database object.
        """
        try:
            if "title" in database:
                return cls._extract_text_from_rich_text(database["title"])

            if "properties" in database and "title" in database["properties"]:
                title_prop = database["properties"]["title"]
                if "title" in title_prop:
                    return cls._extract_text_from_rich_text(title_prop["title"])

            return "Untitled"

        except Exception as e:
            error_msg = f"Error extracting database title: {str(e)}"
            cls.class_logger().warning(error_msg)
            raise DatabaseParsingError(error_msg) from e

    @classmethod
    def _extract_text_from_rich_text(cls, rich_text: List[Dict[str, Any]]) -> str:
        """
        Extract plain text from a rich text array.
        """
        if not rich_text:
            return ""

        text_parts = []
        for text_obj in rich_text:
            if "plain_text" in text_obj:
                text_parts.append(text_obj["plain_text"])

        return "".join(text_parts)
