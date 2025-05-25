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
    PAGE_SIZE = 100
    EARLY_STOP_THRESHOLD = 0.95

    @classmethod
    def from_page_id(cls, page_id: str, token: Optional[str] = None) -> NotionPage:
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
            # Search with pagination and early stopping
            best_match, best_score, all_suggestions = await cls._search_pages_with_matching(
                client, page_name
            )

            # Check if match is good enough
            if best_score < cls.MATCH_THRESHOLD or not best_match:
                suggestion_msg = cls._format_suggestions(all_suggestions)
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

            page = NotionPage.from_page_id(page_id=page_id, token=token)
            cls.logger.info("Successfully created page instance for '%s'", matched_name)

            await client.close()
            return page

        except Exception as e:
            cls.logger.error("Error finding page by name: %s", str(e))
            await client.close()
            raise

    @classmethod
    async def _search_pages_with_matching(
        cls, client: NotionClient, query: str
    ) -> Tuple[Optional[Dict[str, Any]], float, List[str]]:
        """
        Search for pages with pagination and find the best match.
        Includes early stopping for performance optimization.
        """
        cls.logger.debug("Starting paginated search for query: %s", query)
        
        best_match = None
        best_score = 0
        all_suggestions = []
        page_count = 0
        
        # Track suggestions across all pages
        all_matches = []
        
        next_cursor = None
        
        while True:
            # Fetch current page batch
            pages_batch = await cls._fetch_pages_batch(client, next_cursor)
            
            if not pages_batch:
                cls.logger.debug("No more pages to fetch")
                break
                
            pages = pages_batch.get("results", [])
            page_count += len(pages)
            cls.logger.debug("Processing batch of %d pages (total processed: %d)", 
                           len(pages), page_count)
            
            # Process current batch
            batch_match, batch_score, batch_suggestions = cls._find_best_match_in_batch(
                pages, query, best_score
            )
            
            # Update global best if we found a better match
            if batch_score > best_score:
                best_score = batch_score
                best_match = batch_match
                cls.logger.debug("New best match found with score: %.2f", best_score)
            
            # Collect all matches for suggestions
            for page in pages:
                title = cls._extract_title_from_page(page)
                score = SequenceMatcher(None, query.lower(), title.lower()).ratio()
                all_matches.append((title, score))
            
            # Early stopping: if we found a very good match, stop searching
            if best_score >= cls.EARLY_STOP_THRESHOLD:
                cls.logger.info(
                    "Early stopping: found excellent match with score %.2f", best_score
                )
                break
            
            # Check for next page
            next_cursor = pages_batch.get("next_cursor")
            if not next_cursor:
                cls.logger.debug("Reached end of pages")
                break
        
        # Generate final suggestions from all matches
        all_matches.sort(key=lambda x: x[1], reverse=True)
        all_suggestions = [title for title, _ in all_matches[:cls.MAX_SUGGESTIONS]]
        
        cls.logger.info(
            "Search completed. Processed %d pages. Best score: %.2f", 
            page_count, best_score
        )
        
        return best_match, best_score, all_suggestions

    @classmethod
    async def _fetch_pages_batch(
        cls, client: NotionClient, next_cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch a single batch of pages from the Notion API."""
        search_payload = {
            "filter": {"property": "object", "value": "page"},
            "page_size": cls.PAGE_SIZE,
        }
        
        if next_cursor:
            search_payload["start_cursor"] = next_cursor
        
        try:
            response = await client.post("search", search_payload)
            
            if not response:
                cls.logger.error("Empty response from search endpoint")
                return {}
                
            return response
            
        except Exception as e:
            cls.logger.error("Error fetching pages batch: %s", str(e))
            raise

    @classmethod
    def _find_best_match_in_batch(
        cls, pages: List[Dict[str, Any]], query: str, current_best_score: float
    ) -> Tuple[Optional[Dict[str, Any]], float, List[str]]:
        """Find the best matching page in a single batch."""
        batch_best_match = None
        batch_best_score = current_best_score
        
        for page in pages:
            title = cls._extract_title_from_page(page)
            score = SequenceMatcher(None, query.lower(), title.lower()).ratio()
            
            if score > batch_best_score:
                batch_best_score = score
                batch_best_match = page
        
        # Get batch suggestions (not used in the main algorithm but kept for compatibility)
        batch_suggestions = []
        
        return batch_best_match, batch_best_score, batch_suggestions

    @classmethod
    async def _search_pages(cls, client: NotionClient) -> List[Dict[str, Any]]:
        """
        Legacy method - kept for backward compatibility.
        Now uses the paginated approach internally.
        """
        cls.logger.warning(
            "_search_pages is deprecated. Use _search_pages_with_matching instead."
        )
        
        all_pages = []
        next_cursor = None
        
        while True:
            batch = await cls._fetch_pages_batch(client, next_cursor)
            if not batch:
                break
                
            pages = batch.get("results", [])
            all_pages.extend(pages)
            
            next_cursor = batch.get("next_cursor")
            if not next_cursor:
                break
        
        cls.logger.info("Loaded %d total pages", len(all_pages))
        return all_pages

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