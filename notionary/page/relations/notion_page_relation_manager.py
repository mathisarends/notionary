import asyncio
from typing import Any, Dict, List, Optional
from notionary.models.notion_page_response import DatabaseParent, NotionPageResponse
from notionary.page.notion_page_client import NotionPageClient
from notionary.page.relations.notion_page_title_resolver import (
    NotionPageTitleResolver,
)
from notionary.util import LoggingMixin


class NotionPageRelationManager(LoggingMixin):
    """
    Manager for relation properties of a Notion page.
    Manages links between pages and loads available relation options.
    """

    def __init__(
        self, page_id: str, client: NotionPageClient, database_id: Optional[str] = None
    ):
        """
        Initializes the relation manager.
        """
        self._page_id = page_id
        self._client = client
        self._database_id = database_id
        self._page_properties = None

        self._page_title_resolver = NotionPageTitleResolver(client=client)

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

    async def set_relation_values_by_page_titles(
        self, property_name: str, page_titles: List[str]
    ) -> List[str]:
        """
        Sets relation values based on page titles, replacing any existing relations.

        Args:
            property_name: Name of the relation property
            page_titles: List of page titles to set as relations

        Returns:
            List[str]: List of page titles that were successfully set as relations
        """
        self.logger.info(
            "Setting %d relation(s) for property '%s'",
            len(page_titles),
            property_name,
        )

        resolution_results = await asyncio.gather(
            *(
                self._page_title_resolver.get_page_id_by_title(title)
                for title in page_titles
            )
        )

        found_pages = []
        page_ids = []
        not_found_pages = []

        for title, page_id in zip(page_titles, resolution_results):
            if page_id:
                found_pages.append(title)
                page_ids.append(page_id)
                self.logger.debug("Found page ID %s for title '%s'", page_id, title)
            else:
                not_found_pages.append(title)
                self.logger.warning("No page found with title '%s'", title)

        self.logger.debug("Page IDs being sent to API: %s", page_ids)

        if not page_ids:
            self.logger.warning(
                "No valid page IDs found for any of the titles, no changes applied"
            )
            return []

        api_response = await self._set_relations_by_page_ids(property_name, page_ids)

        if not api_response:
            self.logger.error(
                "Failed to set relations for '%s' (API error)", property_name
            )
            return []

        if not_found_pages:
            not_found_str = "', '".join(not_found_pages)
            self.logger.info(
                "Set %d relation(s) for '%s', but couldn't find pages: '%s'",
                len(page_ids),
                property_name,
                not_found_str,
            )
        else:
            self.logger.info(
                "Successfully set all %d relation(s) for '%s'",
                len(page_ids),
                property_name,
            )

        return found_pages

    async def _get_page_properties(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Loads the properties of the page.

        Args:
            force_refresh: If True, a new API call will be made.

        Returns:
            Dict[str, Any]: The properties of the page.
        """
        if self._page_properties is None or force_refresh:
            page_data = await self._client.get_page(self._page_id)
            if page_data:
                self._page_properties = page_data.properties or {}
            else:
                self._page_properties = {}

        return self._page_properties

    async def _set_relations_by_page_ids(
        self, property_name: str, page_ids: List[str]
    ) -> Optional[NotionPageResponse]:
        """
        Adds one or more relations.

        Args:
            property_name: Name of the relation property
            page_ids: List of page IDs to add

        Returns:
            Optional[NotionPageResponse]: API response or None on error
        """
        relation_payload = {"relation": [{"id": page_id} for page_id in page_ids]}

        try:
            page_response: NotionPageResponse = await self._client.patch_page(
                self._page_id,
                {"properties": {property_name: relation_payload}},
            )

            self._page_properties = None

            return page_response
        except Exception as e:
            self.logger.error("Error adding relation: %s", str(e))
            return None
