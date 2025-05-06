from typing import List, Optional, Dict, Any, Tuple
from difflib import SequenceMatcher

from notionary import NotionPage, NotionClient
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import format_uuid, extract_and_validate_page_id


class NotionPageFactory(LoggingMixin):
    """
    Factory class for creating NotionPage instances.
    Provides methods for creating page instances by page ID, URL, or name.
    """

    MATCH_THRESHOLD = 0.6
    MAX_SUGGESTIONS = 5

    @classmethod
    def from_page_id(
        cls, page_id: str, token: Optional[str] = None
    ) -> NotionPage:
        """Create a NotionPage from a page ID."""
        try:
            formatted_id = format_uuid(page_id) or page_id
            page = NotionPage(page_id=formatted_id, token=token)
            cls.logger.info(
                "Successfully created page instance for ID: %s", formatted_id
            )
            return page
        except Exception as e:
            cls.logger.error("Error connecting to page %s: %s", page_id, str(e))
            raise

    @classmethod
    def from_url(cls, url: str, token: Optional[str] = None) -> NotionPage:
        """Create a NotionPage from a Notion URL."""

        try:
            page_id = extract_and_validate_page_id(url=url)
            if not page_id:
                cls.logger.error("Could not extract valid page ID from URL: %s", url)
                raise ValueError(f"Invalid URL: {url}")

            page = NotionPage(page_id=page_id, url=url, token=token)
            cls.logger.info(
                "Successfully created page instance from URL for ID: %s", page_id
            )
            return page
        except Exception as e:
            cls.logger.error("Error connecting to page with URL %s: %s", url, str(e))
            raise

    @classmethod
    async def from_page_name(
        cls, page_name: str, token: Optional[str] = None
    ) -> NotionPage:
        """Create a NotionPage by finding a page with a matching name using fuzzy matching."""
        cls.logger.debug("Searching for page with name: %s", page_name)

        client = NotionClient(token=token)

        try:
            # Fetch pages
            pages = await cls._search_pages(client)
            if not pages:
                cls.logger.warning("No pages found matching '%s'", page_name)
                raise ValueError(f"No pages found matching '{page_name}'")

            # Find best match
            best_match, best_score, suggestions = cls._find_best_match(pages, page_name)

            # Check if match is good enough
            if best_score < cls.MATCH_THRESHOLD or not best_match:
                suggestion_msg = cls._format_suggestions(suggestions)
                cls.logger.warning(
                    "No good match found for '%s'. Best score: %.2f",
                    page_name,
                    best_score,
                )
                raise ValueError(
                    f"No good match found for '{page_name}'. {suggestion_msg}"
                )

            # Create page from best match
            page_id = best_match.get("id")
            if not page_id:
                cls.logger.error("Best match page has no ID")
                raise ValueError("Best match page has no ID")

            matched_name = cls._extract_title_from_page(best_match)
            cls.logger.info(
                "Found matching page: '%s' (ID: %s) with score: %.2f",
                matched_name,
                page_id,
                best_score,
            )

            page = NotionPage(page_id=page_id, title=matched_name, token=token)
            cls.logger.info("Successfully created page instance for '%s'", matched_name)

            await client.close()
            return page

        except Exception as e:
            cls.logger.error("Error finding page by name: %s", str(e))
            await client.close()
            raise

    @classmethod
    async def _search_pages(cls, client: NotionClient) -> List[Dict[str, Any]]:
        """Search for pages using the Notion API."""
        cls.logger.debug("Using search endpoint to find pages")

        search_payload = {
            "filter": {"property": "object", "value": "page"},
            "page_size": 100,
        }

        response = await client.post("search", search_payload)

        if not response or "results" not in response:
            cls.logger.error("Failed to fetch pages using search endpoint")
            raise ValueError("Failed to fetch pages using search endpoint")

        return response.get("results", [])

    @classmethod
    def _find_best_match(
        cls, pages: List[Dict[str, Any]], query: str
    ) -> Tuple[Optional[Dict[str, Any]], float, List[str]]:
        """Find the best matching page for the given query."""
        cls.logger.debug("Found %d pages, searching for best match", len(pages))

        matches = []
        best_match = None
        best_score = 0

        for page in pages:
            title = cls._extract_title_from_page(page)
            score = SequenceMatcher(None, query.lower(), title.lower()).ratio()
            matches.append((page, title, score))

            if score > best_score:
                best_score = score
                best_match = page

        # Get top suggestions
        matches.sort(key=lambda x: x[2], reverse=True)
        suggestions = [title for _, title, _ in matches[: cls.MAX_SUGGESTIONS]]

        return best_match, best_score, suggestions

    @classmethod
    def _format_suggestions(cls, suggestions: List[str]) -> str:
        """Format suggestions as a readable string."""
        if not suggestions:
            return ""

        msg = "Did you mean one of these?\n"
        msg += "\n".join(f"- {suggestion}" for suggestion in suggestions)
        return msg

    @classmethod
    def _extract_title_from_page(cls, page: Dict[str, Any]) -> str:
        """Extract the title from a page object."""
        try:
            if "properties" in page:
                for prop_value in page["properties"].values():
                    if prop_value.get("type") != "title":
                        continue
                    title_array = prop_value.get("title", [])
                    if title_array:
                        return cls._extract_text_from_rich_text(title_array)

            # Fall back to child_page
            if "child_page" in page:
                return page.get("child_page", {}).get("title", "Untitled")

            return "Untitled"

        except Exception as e:
            cls.logger.warning("Error extracting page title: %s", str(e))
            return "Untitled"

    @classmethod
    def _extract_text_from_rich_text(cls, rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text from a rich text array."""
        if not rich_text:
            return ""

        text_parts = [
            text_obj["plain_text"] for text_obj in rich_text if "plain_text" in text_obj
        ]

        return "".join(text_parts)
