import json
from typing import Optional
from notionary.models.notion_page_response import NotionPageResponse
from notionary.notion_client import NotionClient
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

            page_id = self._find_matching_page_in_results(
                search_results.get("results", []), title
            )
            if page_id:
                self.logger.debug(f"Found page with title '{title}' and ID: {page_id}")
                return page_id

            self.logger.debug(f"No page found with title '{title}'")
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
            return self._extract_page_title(page)

        except Exception as e:
            self.logger.error(f"Error retrieving title for page ID '{page_id}': {e}")
            return None

    def _find_matching_page_in_results(
        self, results, search_title: str
    ) -> Optional[str]:
        """
        Extracts and compares page titles from search results to find matching pages.

        Args:
            results: List of search result items from Notion API
            search_title: The title to search for

        Returns:
            Page ID if a match is found, None otherwise
        """
        for result in results:
            page_title = self._extract_page_title(result)
            if not page_title:
                continue

            if page_title == search_title or search_title in page_title:
                return result.get("id")

        return None

    def _extract_page_title(self, page_response: NotionPageResponse) -> str:
        """
        Extract title from page data.

        Args:
            page_response: The page data from Notion API

        Returns:
            str: The extracted title or "Untitled" if not found
        """
        for prop_value in page_response.properties.values():
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

        return "Untitled"
