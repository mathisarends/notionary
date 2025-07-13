from typing import List, Optional, Dict, Any
from difflib import SequenceMatcher

from notionary.database.notion_database import NotionDatabase
from notionary.exceptions.database_exceptions import (
    DatabaseConnectionError,
    DatabaseInitializationError,
    DatabaseNotFoundException,
    NotionDatabaseException,
)
from notionary.util import LoggingMixin
from notionary.util import format_uuid
from notionary.util import singleton


@singleton
class NotionDatabaseFactory(LoggingMixin):
    """
    Factory class for creating NotionDatabaseManager instances.
    Provides methods for creating managers by database ID or name.
    """

    @classmethod
    def from_database_id(
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
        from notionary.search import GlobalSearchService
        
        cls.logger.debug("Searching for database with name: %s", database_name)
        search_service = GlobalSearchService()

        try:
            cls.logger.debug("Using search endpoint to find databases")

            databases = await search_service.search_databases(database_name)

            if not databases:
                cls.logger.warning("No databases found for name: %s", database_name)
                raise DatabaseNotFoundException(database_name)

            cls.logger.debug(
                "Found %d databases, searching for best match", len(databases)
            )

            best_match_db = None
            best_score = 0

            for db in databases:
                title = await db.get_title()
                
                score = SequenceMatcher(
                    None, database_name.lower(), title.lower()
                ).ratio()

                if score > best_score:
                    best_score = score
                    best_match_db = db

            if best_score < 0.6 or not best_match_db:
                error_msg = f"No good database name match found for '{database_name}'. Best match had score {best_score:.2f}"
                cls.logger.warning(error_msg)
                raise DatabaseNotFoundException(database_name, error_msg)

            database_id = best_match_db.database_id
            matched_name = await best_match_db.get_title()

            cls.logger.info(
                "Found matching database: '%s' (ID: %s) with score: %.2f",
                matched_name,
                database_id,
                best_score,
            )

            manager = NotionDatabase(database_id, token)

            cls.logger.info(
                "Successfully created database manager for '%s'", matched_name
            )
            return manager

        except NotionDatabaseException:
            raise
        except Exception as e:
            error_msg = f"Error finding database by name: {str(e)}"
            cls.logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e

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
