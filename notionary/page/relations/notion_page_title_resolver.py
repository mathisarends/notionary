from typing import Optional
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

            for result in search_results.get("results", []):
                properties = result.get("properties", {})
                if not properties:
                    continue

                for prop_value in properties.values():
                    if prop_value.get("type") != "title":
                        continue

                    title_texts = prop_value.get("title", [])
                    if not title_texts:
                        continue

                    page_title = " ".join(
                        [t.get("plain_text", "") for t in title_texts]
                    )

                    if not page_title:
                        continue

                    if page_title == title or title in page_title:
                        self.logger.debug(
                            "Found page: '%s' with ID: %s",
                            page_title,
                            result.get("id"),
                        )
                        return result.get("id")

            self.logger.debug("No page found with title '%s'", title)
            return None

        except Exception as e:
            self.logger.error("Error while searching for page '%s': %s", title, e)
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
            page = await self._client.get(f"pages/{page_id}")
            properties = page.get("properties", {})

            for prop in properties.values():
                if prop.get("type") != "title":
                    continue

                title_parts = prop.get("title", [])
                if not title_parts:
                    continue

                title = " ".join([t.get("plain_text", "") for t in title_parts])
                if title:
                    return title

            self.logger.debug("No title found for page ID '%s'", page_id)
            return None

        except Exception as e:
            self.logger.error("Error retrieving title for page ID '%s': %s", page_id, e)
            return None