import logging
from typing import List, Optional, Dict, Any
from difflib import SequenceMatcher

from notionary import NotionPage, NotionClient
from notionary.util.logging_mixin import LoggingMixin
from notionary.util.page_id_utils import format_uuid, extract_and_validate_page_id


class NotionPageFactory(LoggingMixin):
    """
    Factory class for creating NotionPage instances.
    Provides methods for creating page instances by page ID, URL, or name.
    """

    @classmethod
    def class_logger(cls):
        """Class logger - for class methods"""
        return logging.getLogger(cls.__name__)

    @classmethod
    async def from_page_id(
        cls, page_id: str, token: Optional[str] = None
    ) -> NotionPage:
        """
        Create a NotionPage from a page ID.

        Args:
            page_id: The ID of the Notion page
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionPage instance

        Raises:
            NotionError: If there is any error during page creation or connection
        """
        logger = cls.class_logger()

        try:
            formatted_id = format_uuid(page_id) or page_id

            page = NotionPage(page_id=formatted_id, token=token)

            logger.info("Successfully created page instance for ID: %s", formatted_id)
            return page

        except Exception as e:
            error_msg = f"Error connecting to page {page_id}: {str(e)}"
            logger.error(error_msg)

    @classmethod
    async def from_url(cls, url: str, token: Optional[str] = None) -> NotionPage:
        """
        Create a NotionPage from a Notion URL.

        Args:
            url: The URL of the Notion page
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionPage instance

        Raises:
            NotionError: If there is any error during page creation or connection
        """
        logger = cls.class_logger()

        try:
            page_id = extract_and_validate_page_id(url=url)
            if not page_id:
                error_msg = f"Could not extract valid page ID from URL: {url}"
                logger.error(error_msg)

            page = NotionPage(page_id=page_id, url=url, token=token)

            logger.info(
                "Successfully created page instance from URL for ID: %s", page_id
            )
            return page

        except Exception as e:
            error_msg = f"Error connecting to page with URL {url}: {str(e)}"
            logger.error(error_msg)

    @classmethod
    async def from_page_name(
        cls, page_name: str, token: Optional[str] = None
    ) -> NotionPage:
        """
        Create a NotionPage by finding a page with a matching name.
        Uses fuzzy matching to find the closest match to the given name.
        If no good match is found, suggests closest alternatives ("Did you mean?").

        Args:
            page_name: The name of the Notion page to search for
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            An initialized NotionPage instance

        Raises:
            NotionError: If there is any error during page search or connection
            NotionPageNotFoundError: If no matching page found, includes suggestions
        """
        logger = cls.class_logger()
        logger.debug("Searching for page with name: %s", page_name)

        client = NotionClient(token=token)

        try:
            logger.debug("Using search endpoint to find pages")

            search_payload = {
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            }

            response = await client.post("search", search_payload)

            if not response or "results" not in response:
                error_msg = "Failed to fetch pages using search endpoint"
                logger.error(error_msg)

            pages = response.get("results", [])

            if not pages:
                error_msg = f"No pages found matching '{page_name}'"
                logger.warning(error_msg)

            logger.debug("Found %d pages, searching for best match", len(pages))

            # Store all matches with their scores for potential suggestions
            matches = []
            best_match = None
            best_score = 0

            for page in pages:
                title = cls._extract_title_from_page(page)
                score = SequenceMatcher(None, page_name.lower(), title.lower()).ratio()

                matches.append((page, title, score))

                if score > best_score:
                    best_score = score
                    best_match = page

            if best_score < 0.6 or not best_match:
                # Sort matches by score in descending order
                matches.sort(key=lambda x: x[2], reverse=True)

                # Take top N suggestions (adjust as needed)
                suggestions = [title for _, title, _ in matches[:5]]

                error_msg = f"No good match found for '{page_name}'. Did you mean one of these?\n"
                error_msg += "\n".join(f"- {suggestion}" for suggestion in suggestions)

                logger.warning(
                    "No good match found for '%s'. Best score: %.2f",
                    page_name,
                    best_score,
                )

            page_id = best_match.get("id")

            if not page_id:
                error_msg = "Best match page has no ID"
                logger.error(error_msg)

            matched_name = cls._extract_title_from_page(best_match)

            logger.info(
                "Found matching page: '%s' (ID: %s) with score: %.2f",
                matched_name,
                page_id,
                best_score,
            )

            page = NotionPage(page_id=page_id, title=matched_name, token=token)

            logger.info("Successfully created page instance for '%s'", matched_name)
            await client.close()
            return page

        except Exception as e:
            error_msg = f"Error finding page by name: {str(e)}"
            logger.error(error_msg)

    @classmethod
    def _extract_title_from_page(cls, page: Dict[str, Any]) -> str:
        """
        Extract the title from a page object.

        Args:
            page: The page object returned from the Notion API

        Returns:
            The title of the page

        Raises:
            NotionError: If the title cannot be extracted
        """
        try:
            if "properties" in page:
                for prop_value in page["properties"].values():
                    if prop_value.get("type") != "title":
                        continue
                    title_array = prop_value.get("title", [])
                    if not title_array:
                        continue
                    return cls._extract_text_from_rich_text(title_array)

            if "child_page" in page:
                return page.get("child_page", {}).get("title", "Untitled")

            return "Untitled"

        except Exception as e:
            error_msg = f"Error extracting page title: {str(e)}"
            cls.class_logger().warning(error_msg)
            return "Untitled"

    @classmethod
    def _extract_text_from_rich_text(cls, rich_text: List[Dict[str, Any]]) -> str:
        """
        Extract plain text from a rich text array.

        Args:
            rich_text: A list of rich text objects from the Notion API

        Returns:
            The combined plain text content
        """
        if not rich_text:
            return ""

        text_parts = []
        for text_obj in rich_text:
            if "plain_text" in text_obj:
                text_parts.append(text_obj["plain_text"])

        return "".join(text_parts)


async def demo():
    clipboard = await NotionPageFactory.from_page_name("Jarvis Clipboard")
    icon = await clipboard.get_icon()
    print(f"Icon: {icon}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo())
