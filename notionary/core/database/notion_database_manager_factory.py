import logging
from typing import List, Optional, Dict, Any
from difflib import SequenceMatcher

from notionary.core.notion_client import NotionClient
from notionary.core.database.notion_database_manager import NotionDatabaseManager
from notionary.exceptions.database_exceptions import DatabaseConnectionError, DatabaseInitializationError, DatabaseNotFoundException, DatabaseParsingError, NotionDatabaseException
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.uuid_utils import format_uuid


class NotionDatabaseFactory(LoggingMixin):
    """
    Factory class for creating NotionDatabaseManager instances.
    Provides methods for creating managers by database ID or name.
    """
    
    @classmethod
    def class_logger(cls):
        """Class logger - for class methods"""
        return logging.getLogger(cls.__name__)

    @classmethod
    async def from_database_id(cls, database_id: str, token: Optional[str] = None) -> NotionDatabaseManager:
        """
        Create a NotionDatabaseManager from a database ID.

        Args:
            database_id: The ID of the Notion database
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionDatabaseManager instance
        """
        logger = cls.class_logger()
        
        try:
            formatted_id = format_uuid(database_id) or database_id
            
            manager = NotionDatabaseManager(formatted_id, token)
            
            success = await manager.initialize()
            
            if not success:
                error_msg = f"Failed to initialize database manager for ID: {formatted_id}"
                logger.error(error_msg)
                raise DatabaseInitializationError(formatted_id, error_msg)
                
            logger.info(lambda: f"Successfully created database manager for ID: {formatted_id}")
            return manager
            
        except DatabaseInitializationError:
            # Re-raise the already typed exception
            raise
        except NotionDatabaseException:
            # Re-raise other custom exceptions
            raise
        except Exception as e:
            error_msg = f"Error connecting to database {database_id}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseConnectionError(error_msg) from e

    @classmethod
    async def from_database_name(cls, database_name: str, token: Optional[str] = None) -> NotionDatabaseManager:
        """
        Create a NotionDatabaseManager by finding a database with a matching name.
        Uses fuzzy matching to find the closest match to the given name.

        Args:
            database_name: The name of the Notion database to search for
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionDatabaseManager instance
        """
        logger = cls.class_logger()
        logger.debug(lambda: f"Searching for database with name: {database_name}")
        
        client = NotionClient(token=token)
        
        try:
            logger.debug("Using search endpoint to find databases")
            
            # Create search query for databases
            search_payload = {
                "filter": {
                    "property": "object",
                    "value": "database"
                },
                "page_size": 100
            }
            
            # Perform search
            response = await client.post("search", search_payload)
            
            if not response or "results" not in response:
                error_msg = "Failed to fetch databases using search endpoint"
                logger.error(error_msg)
                raise DatabaseConnectionError(error_msg)
                
            databases = response.get("results", [])
            
            if not databases:
                error_msg = "No databases found"
                logger.warning(error_msg)
                raise DatabaseNotFoundException(database_name, error_msg)
                
            logger.debug(lambda: f"Found {len(databases)} databases, searching for best match")
                
            # Find best match using fuzzy matching
            best_match = None
            best_score = 0
            
            for db in databases:
                title = cls._extract_title_from_database(db)
                    
                score = SequenceMatcher(None, database_name.lower(), title.lower()).ratio()
                    
                if score > best_score:
                    best_score = score
                    best_match = db
            
            # Use a minimum threshold for match quality (0.6 = 60% similarity)
            if best_score < 0.6 or not best_match:
                error_msg = f"No good database name match found for '{database_name}'. Best match had score {best_score:.2f}"
                logger.warning(error_msg)
                raise DatabaseNotFoundException(database_name, error_msg)
                
            database_id = best_match.get("id")
            
            if not database_id:
                error_msg = "Best match database has no ID"
                logger.error(error_msg)
                raise DatabaseParsingError(error_msg)
                
            matched_name = cls._extract_title_from_database(best_match)
            
            logger.info(lambda: f"Found matching database: '{matched_name}' (ID: {database_id}) with score: {best_score:.2f}")
                
            manager = NotionDatabaseManager(database_id, token)
            success = await manager.initialize()
            
            if not success:
                error_msg = f"Failed to initialize database manager for database {database_id}"
                logger.error(error_msg)
                raise DatabaseInitializationError(database_id, error_msg)
                
            logger.info(lambda: f"Successfully created database manager for '{matched_name}'")
            await client.close()
            return manager
            
        except NotionDatabaseException:
            await client.close()
            raise
        except Exception as e:
            error_msg = f"Error finding database by name: {str(e)}"
            logger.error(error_msg)
            await client.close()
            raise DatabaseConnectionError(error_msg) from e

    @classmethod
    def _extract_title_from_database(cls, database: Dict[str, Any]) -> str:
        """
        Extract the title from a database object.
        
        Args:
            database: A database object from the Notion API
            
        Returns:
            The extracted title or "Untitled" if no title is found
            
        Raises:
            DatabaseParsingError: If there's an error parsing the database title
        """
        try:
            # Check for title in the root object
            if "title" in database:
                return cls._extract_text_from_rich_text(database["title"])
            
            # Check for title in properties
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
        
        Args:
            rich_text: A list of rich text objects from Notion API
            
        Returns:
            The concatenated plain text content
        """
        if not rich_text:
            return ""
            
        text_parts = []
        for text_obj in rich_text:
            if "plain_text" in text_obj:
                text_parts.append(text_obj["plain_text"])
        
        return "".join(text_parts)
        
if __name__ == "__main__":
    import asyncio
    
    async def main():
        factory = NotionDatabaseFactory()
        manager = await factory.from_database_name("Projekte")
        
        if manager:
            print(f"Manager created for database: {manager.database_id}")
            await manager.close()
        else:
            print("No matching database found")
    
    asyncio.run(main())