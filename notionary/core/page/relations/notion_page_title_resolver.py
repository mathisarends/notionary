from typing import Optional
from notionary.core.notion_client import NotionClient
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

                for prop_value in properties.values():
                    if prop_value.get("type") == "title":
                        title_texts = prop_value.get("title", [])

                        page_title = " ".join(
                            [t.get("plain_text", "") for t in title_texts]
                        )

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
