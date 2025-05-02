import re
from typing import Any, Dict, List, Optional, Union

from notionary.elements.registry.block_element_registry import BlockElementRegistry
from notionary.elements.registry.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)
from notionary.notion_client import NotionClient
from notionary.page.metadata.metadata_editor import MetadataEditor
from notionary.page.metadata.notion_icon_manager import NotionPageIconManager
from notionary.page.metadata.notion_page_cover_manager import (
    NotionPageCoverManager,
)
from notionary.page.properites.database_property_service import (
    DatabasePropertyService,
)
from notionary.page.relations.notion_page_relation_manager import (
    NotionRelationManager,
)
from notionary.page.content.page_content_manager import PageContentManager
from notionary.page.properites.page_property_manager import PagePropertyManager
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import extract_and_validate_page_id
from notionary.page.relations.page_database_relation import PageDatabaseRelation


class NotionPage(LoggingMixin):
    """
    High-Level Facade for managing content and metadata of a Notion page.
    """

    def __init__(
        self,
        page_id: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self._page_id = extract_and_validate_page_id(page_id=page_id, url=url)
        self._url = url
        self._title = title
        self._client = NotionClient(token=token)
        self._page_data = None
        self._title_loaded = title is not None
        self._url_loaded = url is not None

        self._block_element_registry = (
            BlockElementRegistryBuilder.create_full_registry()
        )

        self._page_content_manager = PageContentManager(
            page_id=self._page_id,
            client=self._client,
            block_registry=self._block_element_registry,
        )
        self._metadata = MetadataEditor(self._page_id, self._client)
        self._page_cover_manager = NotionPageCoverManager(
            page_id=self._page_id, client=self._client
        )
        self._page_icon_manager = NotionPageIconManager(
            page_id=self._page_id, client=self._client
        )

        self._db_relation = PageDatabaseRelation(
            page_id=self._page_id, client=self._client
        )
        self._db_property_service = None

        self._relation_manager = NotionRelationManager(
            page_id=self._page_id, client=self._client
        )

        self._property_manager = PagePropertyManager(
            self._page_id, self._client, self._metadata, self._db_relation
        )

    @property
    def id(self) -> str:
        """
        Get the ID of the page.

        Returns:
            str: The page ID.
        """
        return self._page_id

    @property
    def block_registry(self) -> BlockElementRegistry:
        """
        Get the block element registry associated with this page.

        Returns:
            BlockElementRegistry: The registry of block elements.
        """
        return self._block_element_registry

    @block_registry.setter
    def block_registry(self, block_registry: BlockElementRegistry) -> None:
        """
        Set the block element registry for the page content manager.

        Args:
            block_registry: The registry of block elements to use.
        """
        self._block_element_registry = block_registry
        self._page_content_manager = PageContentManager(
            page_id=self._page_id, client=self._client, block_registry=block_registry
        )

    async def get_title(self) -> str:
        """
        Get the title of the page, loading it if necessary.

        Returns:
            str: The page title.
        """
        if not self._title_loaded:
            await self._load_page_title()
        return self._title

    async def get_url(self) -> str:
        """
        Get the URL of the page, constructing it if necessary.

        Returns:
            str: The page URL.
        """
        if not self._url_loaded:
            self._url = await self._build_notion_url()
            self._url_loaded = True
        return self._url

    async def append_markdown(self, markdown: str) -> str:
        """
        Append markdown content to the page.

        Args:
            markdown: The markdown content to append.

        Returns:
            str: Status or confirmation message.
        """
        return await self._page_content_manager.append_markdown(markdown_text=markdown)

    async def clear(self) -> str:
        """
        Clear all content from the page.

        Returns:
            str: Status or confirmation message.
        """
        return await self._page_content_manager.clear()

    async def replace_content(self, markdown: str) -> str:
        """
        Replace the entire page content with new markdown content.

        Args:
            markdown: The new markdown content.

        Returns:
            str: Status or confirmation message.
        """
        await self._page_content_manager.clear()
        return await self._page_content_manager.append_markdown(markdown)

    async def get_text(self) -> str:
        """
        Get the text content of the page.

        Returns:
            str: The text content of the page.
        """
        return await self._page_content_manager.get_text()

    async def set_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Set the title of the page.

        Args:
            title: The new title.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        result = await self._metadata.set_title(title)
        if result:
            self._title = title
            self._title_loaded = True
        return result

    async def set_page_icon(
        self, emoji: Optional[str] = None, external_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Set the icon for the page. Provide either emoji or external_url.

        Args:
            emoji: Optional emoji to use as icon.
            external_url: Optional URL to an external image to use as icon.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._page_icon_manager.set_icon(emoji, external_url)

    async def get_icon(self) -> Optional[str]:
        """
        Retrieve the page icon - either emoji or external URL.

        Returns:
            Optional[str]: The icon emoji or URL, or None if no icon is set.
        """
        return await self._page_icon_manager.get_icon()

    async def get_cover_url(self) -> str:
        """
        Get the URL of the page cover image.

        Returns:
            str: The URL of the cover image or empty string if not available.
        """
        return await self._page_cover_manager.get_cover_url()

    async def set_page_cover(self, external_url: str) -> Optional[Dict[str, Any]]:
        """
        Set the cover image for the page using an external URL.

        Args:
            external_url: URL to the external image.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._page_cover_manager.set_cover(external_url)

    async def set_random_gradient_cover(self) -> Optional[Dict[str, Any]]:
        """
        Set a random gradient as the page cover.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._page_cover_manager.set_random_gradient_cover()

    async def get_properties(self) -> Dict[str, Any]:
        """
        Retrieve all properties of the page.

        Returns:
            Dict[str, Any]: Dictionary of property names and their values.
        """
        return await self._property_manager.get_properties()

    async def get_property_value(self, property_name: str) -> Any:
        """
        Get the value of a specific property.

        Args:
            property_name: The name of the property.

        Returns:
            Any: The value of the property.
        """
        return await self._property_manager.get_property_value(
            property_name, self._relation_manager.get_relation_values
        )

    async def set_property_by_name(
        self, property_name: str, value: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Set the value of a specific property by its name.

        Args:
            property_name: The name of the property.
            value: The new value to set.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._property_manager.set_property_by_name(
            property_name=property_name,
            value=value,
        )

    async def is_database_page(self) -> bool:
        """
        Check if this page belongs to a database.

        Returns:
            bool: True if the page belongs to a database, False otherwise.
        """
        return await self._db_relation.is_database_page()

    async def get_parent_database_id(self) -> Optional[str]:
        """
        Get the ID of the database this page belongs to, if any.

        Returns:
            Optional[str]: The database ID or None if the page doesn't belong to a database.
        """
        return await self._db_relation.get_parent_database_id()

    async def get_available_options_for_property(self, property_name: str) -> List[str]:
        """
        Get the available option names for a property (select, multi_select, status).

        Args:
            property_name: The name of the property.

        Returns:
            List[str]: List of available option names.
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_option_names(property_name)
        return []

    async def get_property_type(self, property_name: str) -> Optional[str]:
        """
        Get the type of a specific property.

        Args:
            property_name: The name of the property.

        Returns:
            Optional[str]: The type of the property or None if not found.
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_property_type(property_name)
        return None

    async def get_database_metadata(
        self, include_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get complete metadata about the database this page belongs to.

        Args:
            include_types: Optional list of property types to include. If None, all properties are included.

        Returns:
            Dict[str, Any]: Database metadata or empty dict if not a database page.
        """
        db_service = await self._get_db_property_service()
        if db_service:
            return await db_service.get_database_metadata(include_types)
        return {"properties": {}}

    async def get_relation_options(
        self, property_name: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Return available options for a relation property.

        Args:
            property_name: The name of the relation property.
            limit: Maximum number of options to return.

        Returns:
            List[Dict[str, Any]]: List of available relation options.
        """
        return await self._relation_manager.get_relation_options(property_name, limit)

    async def add_relations_by_name(
        self, relation_property_name: str, page_titles: Union[str, List[str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Add one or more relations to a relation property.

        Args:
            relation_property_name: The name of the relation property.
            page_titles: One or more page titles to relate to.

        Returns:
            Optional[Dict[str, Any]]: Response data from the API if successful, None otherwise.
        """
        return await self._relation_manager.add_relation_by_name(
            property_name=relation_property_name, page_titles=page_titles
        )

    async def get_relation_values(self, property_name: str) -> List[str]:
        """
        Return the current relation values for a property.

        Args:
            property_name: The name of the relation property.

        Returns:
            List[str]: List of relation values.
        """
        return await self._relation_manager.get_relation_values(property_name)

    async def get_relation_property_ids(self) -> List[str]:
        """
        Return a list of all relation property names.

        Returns:
            List[str]: List of relation property names.
        """
        return await self._relation_manager.get_relation_property_ids()

    async def get_all_relations(self) -> Dict[str, List[str]]:
        """
        Return all relation properties and their values.

        Returns:
            Dict[str, List[str]]: Dictionary mapping relation property names to their values.
        """
        return await self._relation_manager.get_all_relations()

    async def get_last_edited_time(self) -> str:
        """
        Get the timestamp when the page was last edited.

        Returns:
            str: ISO 8601 formatted timestamp string of when the page was last edited.
        """
        try:
            page_data = await self._client.get_page(self._page_id)
            if "last_edited_time" in page_data:
                return page_data["last_edited_time"]

            self.logger.warning("last_edited_time not found in page data")
            return ""

        except Exception as e:
            self.logger.error("Error retrieving last edited time: %s", str(e))
            return ""

    async def _load_page_title(self) -> str:
        """
        Load the page title from Notion API if not already loaded.

        Returns:
            str: The page title.
        """
        if self._title is not None:
            return self._title

        self.logger.debug("Lazy loading page title for page: %s", self._page_id)
        try:
            # Retrieve page data
            page_data = await self._client.get(f"pages/{self._page_id}")
            self._title = self._extract_title_from_page_data(page_data)
        except Exception as e:
            self.logger.error("Error loading page title: %s", str(e))
            self._title = "Untitled"

        self._title_loaded = True
        self.logger.debug("Loaded page title: %s", self._title)
        return self._title

    def _extract_title_from_page_data(self, page_data: Dict[str, Any]) -> str:
        """
        Extract title from page data.

        Args:
            page_data: The page data from Notion API

        Returns:
            str: The extracted title or "Untitled" if not found
        """
        if "properties" not in page_data:
            return "Untitled"

        for prop_value in page_data["properties"].values():
            if prop_value.get("type") != "title":
                continue

            title_array = prop_value.get("title", [])
            if not title_array:
                continue

            text_parts = []
            for text_obj in title_array:
                if "plain_text" in text_obj:
                    text_parts.append(text_obj["plain_text"])

            return "".join(text_parts) or "Untitled"

        return "Untitled"

    async def _build_notion_url(self) -> str:
        """
        Build a Notion URL from the page ID, including the title if available.

        Returns:
            str: The Notion URL for the page.
        """
        title = await self._load_page_title()

        url_title = ""
        if title and title != "Untitled":
            url_title = re.sub(r"[^\w\s-]", "", title)
            url_title = re.sub(r"[\s]+", "-", url_title)
            url_title = f"{url_title}-"

        clean_id = self._page_id.replace("-", "")

        return f"https://www.notion.so/{url_title}{clean_id}"

    async def _get_db_property_service(self) -> Optional[DatabasePropertyService]:
        """
        Gets the database property service, initializing it if necessary.
        This is a more intuitive way to work with the instance variable.

        Returns:
            Optional[DatabasePropertyService]: The database property service or None if not applicable
        """
        if self._db_property_service is not None:
            return self._db_property_service

        database_id = await self._db_relation.get_parent_database_id()
        if not database_id:
            return None

        self._db_property_service = DatabasePropertyService(database_id, self._client)
        await self._db_property_service.load_schema()
        return self._db_property_service
