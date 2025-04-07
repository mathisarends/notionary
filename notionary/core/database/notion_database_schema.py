from typing import AsyncGenerator, Dict, List, Optional, Any, TypedDict, Union, cast, Literal
from notionary.core.notion_client import NotionClient
from notionary.core.page.notion_page_manager import NotionPageManager
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.singleton_decorator import singleton


class NotionTextContent(TypedDict):
    plain_text: str


class NotionTitleProperty(TypedDict):
    type: Literal["title"]
    title: List[NotionTextContent]


class NotionSelectOption(TypedDict):
    name: str
    id: Optional[str]
    color: Optional[str]


class NotionSelectProperty(TypedDict):
    type: Literal["select"]
    select: Dict[str, List[NotionSelectOption]]


class NotionMultiSelectProperty(TypedDict):
    type: Literal["multi_select"]
    multi_select: Dict[str, List[NotionSelectOption]]


class NotionStatusProperty(TypedDict):
    type: Literal["status"]
    status: Dict[str, List[NotionSelectOption]]


class NotionRelationProperty(TypedDict):
    type: Literal["relation"]
    relation: Dict[str, str]


class NotionNumberProperty(TypedDict):
    type: Literal["number"]
    number: Dict[str, Any]


NotionPropertyType = Union[
    NotionTitleProperty,
    NotionSelectProperty,
    NotionMultiSelectProperty,
    NotionStatusProperty,
    NotionRelationProperty,
    NotionNumberProperty,
    Dict[str, Any],  # Fallback
]


class RelationOption(TypedDict):
    id: str
    title: str


@singleton
class NotionDatabaseRegistry(LoggingMixin):
    """
    Registry that maintains a mapping of database IDs to their titles.
    Provides a simple way to lookup databases by ID or title.
    """

    def __init__(self, client: NotionClient) -> None:
        """
        Initialize the registry with a NotionClient.
        """
        self._client = client
        self._id_to_title: Dict[str, str] = {}
        self._title_to_id: Dict[str, str] = {}
        self._initialized: bool = False


    async def initialize(self) -> None:
        """
        Load all databases and build the ID-to-title mapping.
        """
        if self._initialized:
            return

        self.logger.info("Initializing database registry...")
        
        # Reset mappings
        self._id_to_title.clear()
        self._title_to_id.clear()
        
        count = 0
        async for db in self.iter_databases():
            db_id = db.get("id")
            if not db_id:
                continue

            db_title = self._extract_database_title(db)
            self._id_to_title[db_id] = db_title
            count += 1

            if db_title in self._title_to_id:
                self.logger.warning("Duplicate database title found: %s", db_title)
                self._title_to_id[f"{db_title} ({db_id})"] = db_id
            else:
                self._title_to_id[db_title] = db_id

        self._initialized = True
        self.logger.info(
            "Database registry initialized with %d databases", count
        )

    async def get_title(self, database_id: str) -> Optional[str]:
        """
        Get the title of a database by its ID.
        """
        if not self._initialized:
            await self.initialize()

        return self._id_to_title.get(database_id)

    async def get_id(self, title: str) -> Optional[str]:
        """
        Get the ID of a database by its title.
        """
        if not self._initialized:
            await self.initialize()

        return self._title_to_id.get(title)

    async def get_all_ids(self) -> List[str]:
        """
        Get all database IDs.
        """
        if not self._initialized:
            await self.initialize()

        return list(self._id_to_title.keys())

    async def get_all_titles(self) -> List[str]:
        """
        Get all database titles.
        """
        if not self._initialized:
            await self.initialize()

        return list(self._title_to_id.keys())

    async def get_id_title_map(self) -> Dict[str, str]:
        """
        Get the complete mapping of database IDs to titles.

        Returns:
            A dictionary mapping database IDs to titles
        """
        if not self._initialized:
            await self.initialize()

        return self._id_to_title.copy()

    async def refresh(self) -> None:
        """
        Refresh the registry by reloading all databases.
        """
        self._id_to_title.clear()
        self._title_to_id.clear()
        self._initialized = False
        await self.initialize()

    def _extract_database_title(self, database: Dict[str, Any]) -> str:
        """
        Extract the database title from a Notion API response.

        Args:
            database: The database object from the Notion API

        Returns:
            The extracted title or "Untitled" if no title is found
        """
        title = "Untitled"

        if "title" in database:
            title_parts: List[str] = []
            for text_obj in database["title"]:
                if "plain_text" in text_obj:
                    title_parts.append(text_obj["plain_text"])

            if title_parts:
                title = "".join(title_parts)

        return title
    
    
    async def iter_databases(self, page_size: int = 100) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Asynchronous generator that yields Notion databases one by one.
        
        Uses the Notion API to provide paginated access to all databases
        without loading all of them into memory at once.
        
        Args:
            page_size: The number of databases to fetch per request
            
        Yields:
            Individual database objects from the Notion API
        """
        start_cursor: Optional[str] = None
        
        while True:
            body: Dict[str, Any] = {
                "filter": {"value": "database", "property": "object"},
                "page_size": page_size,
            }
            
            if start_cursor:
                body["start_cursor"] = start_cursor
                
            result = await self._client.post("search", data=body)
            
            if not result or "results" not in result:
                self.logger.error("Error fetching databases")
                break
                
            for database in result["results"]:
                yield database
                
            if "has_more" in result and result["has_more"] and "next_cursor" in result:
                start_cursor = result["next_cursor"]
            else:
                break

class NotionDatabaseSchema:
    """
    Represents the schema of a specific Notion database.
    Manages property information, options, and relations for a single database.
    """

    def __init__(self, database_id: str, client: NotionClient) -> None:
        """
        Initialize a database schema handler for a specific database.

        Args:
            database_id: The ID of the database
            client: An instance of NotionClient for API requests
        """
        self.database_id: str = database_id
        self._client: NotionClient = client
        self._properties: Dict[str, NotionPropertyType] = {}
        self._loaded: bool = False

    async def load(self) -> bool:
        """
        Load the database schema from the Notion API.

        Returns:
            True if the schema was loaded successfully, False otherwise
        """
        if self._loaded:
            return True

        db_details = await self._client.get(f"databases/{self.database_id}")
        if not db_details or "properties" not in db_details:
            return False

        self._properties = db_details["properties"]
        self._loaded = True
        return True

    async def get_property_types(self) -> Dict[str, str]:
        """
        Get a mapping of property names to their types.

        Returns:
            A dictionary mapping property names to types
        """
        if not self._loaded:
            await self.load()

        return {name: prop.get("type", "") for name, prop in self._properties.items()}

    async def get_select_options(self, property_name: str) -> List[NotionSelectOption]:
        """
        Get the options for a select, multi_select, or status property.

        Args:
            property_name: The name of the property

        Returns:
            A list of option objects
        """
        if not self._loaded:
            await self.load()

        if property_name not in self._properties:
            return []

        prop = self._properties[property_name]
        prop_type = prop.get("type", "")

        if prop_type not in ["select", "multi_select", "status"]:
            return []

        if prop_type in prop and "options" in prop[prop_type]:
            return cast(List[NotionSelectOption], prop[prop_type]["options"])

        return []

    async def get_relation_options(
        self, property_name: str, limit: int = 100
    ) -> List[RelationOption]:
        """
        Get available options for a relation property (pages in the related database).

        Args:
            property_name: The name of the relation property
            limit: Maximum number of options to retrieve

        Returns:
            List of options with id and title
        """
        related_db_id = await self.get_relation_database_id(property_name)
        if not related_db_id:
            return []

        pages = await self._query_database_pages(related_db_id, limit)
        return self._extract_page_titles_and_ids(pages)

    async def get_relation_database_id(self, property_name: str) -> Optional[str]:
        """
        Get the ID of the related database for a relation property.

        Args:
            property_name: The name of the property

        Returns:
            The ID of the related database or None
        """
        if not self._loaded:
            await self.load()

        if property_name not in self._properties:
            return None

        prop = self._properties[property_name]
        prop_type = prop.get("type", "")

        if prop_type != "relation" or "relation" not in prop:
            return None

        relation_prop = cast(NotionRelationProperty, prop)
        return relation_prop["relation"].get("database_id")

    def _extract_page_titles_and_ids(
        self, pages: List[Dict[str, Any]]
    ) -> List[RelationOption]:
        """
        Extract titles and IDs from page objects.

        Args:
            pages: List of page objects from the Notion API

        Returns:
            List of dictionaries with id and title for each page
        """
        options: List[RelationOption] = []

        for page in pages:
            page_id = page.get("id")
            if not page_id:
                continue

            page_title = self.extract_title_from_page(page)
            options.append({"id": page_id, "title": page_title})

        return options

    def extract_title_from_page(self, page: Dict[str, Any]) -> str:
        """
        Extract the title from a page object.

        Args:
            page: A page object from the Notion API

        Returns:
            The extracted title or "Untitled" if no title is found
        """
        properties = page.get("properties", {})

        # Find the title property (usually the one with type "title")
        for prop_data in properties.values():
            if prop_data.get("type") != "title" or "title" not in prop_data:
                continue

            title_property = cast(NotionTitleProperty, prop_data)
            title_content = title_property["title"]
            if not title_content or not isinstance(title_content, list):
                continue

            title_parts: List[str] = []
            for part in title_content:
                if "plain_text" in part:
                    title_parts.append(part["plain_text"])

            if title_parts:
                return "".join(title_parts)

        return "Untitled"

    async def _query_database_pages(
        self, database_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Returns:
            List of page objects from the Notion API
        """
        pages: List[Dict[str, Any]] = []
        count = 0
        
        async for page in self.iter_database_pages(database_id=database_id, page_size=min(limit, 100)):
            pages.append(page)
            count += 1
            
            if count >= limit:
                break
                
        return pages
    
    async def iter_database_pages(
        self, 
        database_id: Optional[str] = None, 
        page_size: int = 100,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[NotionPageManager, None]:
        """
        Asynchronous generator that yields pages from a Notion database one by one.
        
        Uses the Notion API to provide paginated access to all pages in a database
        without loading all of them into memory at once.
        
        Args:
            database_id: The ID of the database to query (uses self.database_id if None)
            page_size: The number of pages to fetch per request
            filter_conditions: Optional filter to apply to the database query
            sorts: Optional sort instructions for the database query
            
        Yields:
            Individual page objects from the Notion API
        """
        db_id = database_id or self.database_id
        if not db_id:
            raise ValueError("No database ID provided")
        
        start_cursor: Optional[str] = None
        has_more = True
        
        body: Dict[str, Any] = {"page_size": page_size}
        
        if filter_conditions:
            body["filter"] = filter_conditions
            
        if sorts:
            body["sorts"] = sorts
        
        while has_more:
            current_body = body.copy() 
            if start_cursor:
                current_body["start_cursor"] = start_cursor
                
            result = await self._client.post(f"databases/{db_id}/query", data=current_body)
            
            if not result or "results" not in result:
                return
            
            for page in result["results"]:
                notion_page_manager = NotionPageManager(page_id=page.get("id", ""), title=page.get("title", ""))
                yield notion_page_manager
            
            has_more = result.get("has_more", False)
            start_cursor = result.get("next_cursor") if has_more else None