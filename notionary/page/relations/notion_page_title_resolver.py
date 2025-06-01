from typing import Optional, Dict, Any, List
from notionary import NotionClient
from notionary.util.logging_mixin import LoggingMixin


class NotionPageTitleResolver(LoggingMixin):
    def __init__(self, client: NotionClient):
        self._client = client

    async def get_page_id_by_title(self, title: str) -> Optional[str]:
        """
        Searches for a Notion page by its title and returns the corresponding page ID if found.
        """
        try:
            search_results = await self._client.post(
                "search",
                {"query": title, "filter": {"value": "page", "property": "object"}},
            )

            results = search_results.get("results", [])

            if not results:
                self.logger.debug(f"No page found with title '{title}'")
                return None

            # Durchsuche die Ergebnisse nach dem passenden Titel
            for result in results:
                properties = result.get("properties", {})
                page_title = self._extract_page_title_from_properties(properties)

                if page_title == title:
                    return result.get("id")

            self.logger.debug(f"No matching page found with title '{title}'")
            return None

        except Exception as e:
            self.logger.error(f"Error while searching for page '{title}': {e}")
            return None

    async def get_title_by_page_id(self, page_id: str) -> Optional[str]:
        """
        Retrieves the title of a Notion page by its page ID.

        Args:
            page_id: The ID of the Notion page.

        Returns:
            The title of the page, or None if not found.
        """
        try:
            page = await self._client.get_page(page_id)
            return self._extract_page_title_from_properties(page.properties)

        except Exception as e:
            self.logger.error(f"Error retrieving title for page ID '{page_id}': {e}")
            return None

    async def get_page_titles_by_ids(self, page_ids: List[str]) -> Dict[str, str]:
        """
        Retrieves titles for multiple page IDs at once.

        Args:
            page_ids: List of page IDs to get titles for

        Returns:
            Dictionary mapping page IDs to their titles
        """
        result = {}
        for page_id in page_ids:
            title = await self.get_title_by_page_id(page_id)
            if title:
                result[page_id] = title
        return result

    def _extract_page_title_from_properties(self, properties: Dict[str, Any]) -> str:
        """
        Extract title from properties dictionary.

        Args:
            properties: The properties dictionary from a Notion page

        Returns:
            str: The extracted title or "Untitled" if not found
        """
        try:
            for prop_value in properties.values():
                if not isinstance(prop_value, dict):
                    continue

                if prop_value.get("type") != "title":
                    continue

                title_array = prop_value.get("title", [])
                if not title_array:
                    continue

                for text_obj in title_array:
                    if "plain_text" in text_obj:
                        return text_obj["plain_text"]
        except Exception as e:
            self.logger.error(f"Error extracting page title from properties: {e}")

        return "Untitled"
