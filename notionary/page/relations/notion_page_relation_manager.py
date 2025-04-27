from typing import Any, Dict, List, Optional
from notionary.notion_client import NotionClient
from notionary.page.relations.notion_page_title_resolver import (
    NotionPageTitleResolver,
)
from notionary.page.relations.relation_operation_result import (
    RelationOperationResult,
)
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import is_valid_uuid


class NotionRelationManager(LoggingMixin):
    """
    Manager for relation properties of a Notion page.
    Manages links between pages and loads available relation options.
    """

    def __init__(
        self, page_id: str, client: NotionClient, database_id: Optional[str] = None
    ):
        """
        Initializes the relation manager.

        Args:
            page_id: ID of the Notion page
            client: NotionClient instance
            database_id: Optional, ID of the database the page belongs to (loaded if needed)
        """
        self._page_id = page_id
        self._client = client
        self._database_id = database_id
        self._page_properties = None

        self._page_title_resolver = NotionPageTitleResolver(client=client)

    async def _get_page_properties(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Loads the properties of the page.

        Args:
            force_refresh: If True, a fresh API call will be made

        Returns:
            Dict[str, Any]: The properties of the page
        """
        if self._page_properties is None or force_refresh:
            page_data = await self._client.get_page(self._page_id)
            if page_data and "properties" in page_data:
                self._page_properties = page_data["properties"]
            else:
                self._page_properties = {}

        return self._page_properties

    async def _ensure_database_id(self) -> Optional[str]:
        """
        Ensures the database_id is available. Loads it if necessary.

        Returns:
            Optional[str]: The database ID or None
        """
        if self._database_id:
            return self._database_id

        page_data = await self._client.get_page(self._page_id)
        if page_data and "parent" in page_data:
            parent = page_data["parent"]
            if parent.get("type") == "database_id":
                self._database_id = parent.get("database_id")
                return self._database_id

        return None

    async def get_relation_property_ids(self) -> List[str]:
        """
        Returns a list of all relation property names.

        Returns:
            List[str]: Names of all relation properties
        """
        properties = await self._get_page_properties()

        return [
            prop_name
            for prop_name, prop_data in properties.items()
            if prop_data.get("type") == "relation"
        ]

    async def get_relation_values(self, property_name: str) -> List[str]:
        """
        Returns the titles of the pages linked via a relation property.

        Args:
            property_name: Name of the relation property

        Returns:
            List[str]: List of linked page titles
        """
        properties = await self._get_page_properties()

        if property_name not in properties:
            return []

        prop_data = properties[property_name]

        if prop_data.get("type") != "relation" or "relation" not in prop_data:
            return []

        resolver = NotionPageTitleResolver(self._client)
        titles = []

        for rel in prop_data["relation"]:
            page_id = rel.get("id")
            if not page_id:
                continue

            title = await resolver.get_title_by_page_id(page_id)
            if not title:
                continue

            titles.append(title)

        return titles

    async def get_relation_details(
        self, property_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Returns details about the relation property, including the linked database.

        Args:
            property_name: Name of the relation property

        Returns:
            Optional[Dict[str, Any]]: Relation details or None
        """
        database_id = await self._ensure_database_id()
        if not database_id:
            return None

        try:
            database = await self._client.get(f"databases/{database_id}")
            if not database or "properties" not in database:
                return None

            properties = database["properties"]

            if property_name not in properties:
                return None

            prop_data = properties[property_name]

            if prop_data.get("type") != "relation":
                return None

            return prop_data.get("relation", {})

        except Exception as e:
            self.logger.error("Error retrieving relation details: %s", str(e))
            return None

    async def get_relation_database_id(self, property_name: str) -> Optional[str]:
        """
        Returns the ID of the linked database for a relation property.

        Args:
            property_name: Name of the relation property

        Returns:
            Optional[str]: ID of the linked database or None
        """
        relation_details = await self.get_relation_details(property_name)

        if not relation_details:
            return None

        return relation_details.get("database_id")

    async def get_relation_options(
        self, property_name: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Returns available options for a relation property.

        Args:
            property_name: Name of the relation property
            limit: Maximum number of options to return

        Returns:
            List[Dict[str, Any]]: List of available options with ID and name
        """
        related_db_id = await self.get_relation_database_id(property_name)

        if not related_db_id:
            return []

        try:
            query_result = await self._client.post(
                f"databases/{related_db_id}/query",
                {
                    "page_size": limit,
                },
            )

            if not query_result or "results" not in query_result:
                return []

            options = []
            for page in query_result["results"]:
                page_id = page.get("id")
                title = self._extract_title_from_page(page)

                if page_id and title:
                    options.append({"id": page_id, "name": title})

            return options
        except Exception as e:
            self.logger.error("Error retrieving relation options: %s", str(e))
            return []

    def _extract_title_from_page(self, page: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the title from a page object.

        Args:
            page: The page object from the Notion API

        Returns:
            Optional[str]: The page title or None
        """
        if "properties" not in page:
            return None

        properties = page["properties"]

        for prop_data in properties.values():
            if prop_data.get("type") == "title" and "title" in prop_data:
                title_parts = prop_data["title"]
                return "".join(
                    [text_obj.get("plain_text", "") for text_obj in title_parts]
                )

        return None

    async def add_relation(
        self, property_name: str, page_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Adds one or more relations.

        Args:
            property_name: Name of the relation property
            page_ids: List of page IDs to add

        Returns:
            Optional[Dict[str, Any]]: API response or None on error
        """
        existing_relations = await self.get_relation_values(property_name) or []

        all_relations = list(set(existing_relations + page_ids))

        relation_payload = {"relation": [{"id": page_id} for page_id in all_relations]}

        try:
            result = await self._client.patch(
                f"pages/{self._page_id}",
                {"properties": {property_name: relation_payload}},
            )

            self._page_properties = None

            return result
        except Exception as e:
            self.logger.error("Error adding relation: %s", str(e))
            return None

    async def add_relation_by_name(
        self, property_name: str, page_titles: List[str]
    ) -> RelationOperationResult:
        """
        Adds one or more relations based on page titles.

        Args:
            property_name: Name of the relation property
            page_titles: List of page titles to link

        Returns:
            RelationOperationResult: Result of the operation with details on which pages were found and added
        """
        found_pages = []
        not_found_pages = []
        page_ids = []

        self.logger.info(
            "Attempting to add %d relation(s) to property '%s'",
            len(page_titles),
            property_name,
        )

        for page in page_titles:
            if is_valid_uuid(page):
                page_ids.append(page)
                found_pages.append(page)
                self.logger.debug("Using page ID directly: %s", page)
            else:
                page_id = await self._page_title_resolver.get_page_id_by_title(page)
                if page_id:
                    page_ids.append(page_id)
                    found_pages.append(page)
                    self.logger.debug("Found page ID %s for title '%s'", page_id, page)
                else:
                    not_found_pages.append(page)
                    self.logger.warning("No page found with title '%s'", page)

        if not page_ids:
            self.logger.warning(
                "No valid page IDs found for any of the titles, no changes applied"
            )
            return RelationOperationResult.from_no_pages_found(
                property_name, not_found_pages
            )

        api_response = await self.add_relation(property_name, page_ids)

        if api_response:
            result = RelationOperationResult.from_success(
                property_name=property_name,
                found_pages=found_pages,
                not_found_pages=not_found_pages,
                page_ids_added=page_ids,
                api_response=api_response,
            )

            if not_found_pages:
                not_found_str = "', '".join(not_found_pages)
                self.logger.info(
                    "Added %d relation(s) to '%s', but couldn't find pages: '%s'",
                    len(page_ids),
                    property_name,
                    not_found_str,
                )
            else:
                self.logger.info(
                    "Successfully added all %d relation(s) to '%s'",
                    len(page_ids),
                    property_name,
                )

            return result

        self.logger.error("Failed to add relations to '%s' (API error)", property_name)
        return RelationOperationResult.from_no_api_response(
            property_name=property_name,
            found_pages=found_pages,
            page_ids_added=page_ids,
        )

    async def set_relations(
        self, property_name: str, page_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Sets the relations to the specified IDs (replaces existing ones).

        Args:
            property_name: Name of the relation property
            page_ids: List of page IDs to set

        Returns:
            Optional[Dict[str, Any]]: API response or None on error
        """
        relation_payload = {"relation": [{"id": page_id} for page_id in page_ids]}

        try:
            result = await self._client.patch(
                f"pages/{self._page_id}",
                {"properties": {property_name: relation_payload}},
            )

            self._page_properties = None

            return result
        except Exception as e:
            self.logger.error("Error setting relations: %s", str(e))
            return None

    async def get_all_relations(self) -> Dict[str, List[str]]:
        """Returns all relation properties and their values."""
        relation_properties = await self.get_relation_property_ids()

        if not relation_properties:
            return {}

        result = {}
        for prop_name in relation_properties:
            result[prop_name] = await self.get_relation_values(prop_name)

        return result
