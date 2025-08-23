from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Optional

from notionary.util import format_uuid
from notionary.util.fuzzy import find_best_match


# TODO: Implement users lookup here aswell and use in @TextInlineForatter
# Write testst then
class NameIdResolver:
    """
    Bidirectional resolver for Notion page and database names and IDs.
    """

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        search_limit: int = 10,
    ):
        """
        Initialize the resolver with a Notion workspace.
        """
        from notionary import NotionWorkspace

        self.workspace = NotionWorkspace(token=token)
        self.search_limit = search_limit

    async def resolve_id(self, name: str) -> Optional[str]:
        """
        Convert a page or database name to its Notion ID.
        """
        if not name:
            return None

        cleaned_name = name.strip()

        # Return if already a valid Notion ID (handles both UUID formats)
        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        # First try to find a page
        page_id = await self._resolve_page_id(cleaned_name)
        if page_id:
            return page_id

        # Fallback: try to find a database
        database_id = await self._resolve_database_id(cleaned_name)
        return database_id

    async def resolve_name(self, id: str) -> Optional[str]:
        """
        Convert a Notion page or database ID to its human-readable name.

        Args:
            id: Notion page or database ID to resolve

        Returns:
            Page or database title/name if found, None if not found or inaccessible
        """
        from notionary import NotionDatabase
        from notionary import NotionPage

        if not id:
            return None

        # Validate and format UUID
        formatted_id = format_uuid(id)
        if not formatted_id:
            return None

        # Try page first (suppress expected validation error logs)
        with self._suppress_expected_errors():
            try:
                page = await NotionPage.from_page_id(formatted_id)
                return page.title
            except Exception:
                # Expected: ID might be a database, not a page
                pass

        # Try database (suppress expected validation error logs)
        with self._suppress_expected_errors():
            try:
                database = await NotionDatabase.from_database_id(formatted_id)
                return database.title
            except Exception:
                # Expected: ID might not exist or be inaccessible
                return None

    async def resolve_database_name(self, name: str) -> Optional[str]:
        """
        Convert a database name to its Notion database ID.
        Specifically searches only databases, not pages.
        """
        if not name:
            return None

        cleaned_name = name.strip()

        # Return if already a valid Notion ID (handles both UUID formats)
        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        # Search specifically for databases only
        return await self._resolve_database_id(cleaned_name)

    @contextmanager
    def _suppress_expected_errors(self):
        """
        Context manager to temporarily suppress expected validation error logs
        from BaseNotionClient HTTP requests when trying wrong ID types.
        """
        # Get all relevant loggers that might log HTTP validation errors
        loggers_to_suppress = [
            logging.getLogger("NotionPageClient"),
            logging.getLogger("NotionDatabaseClient"),
            logging.getLogger("BaseNotionClient"),
            logging.getLogger("notionary"),
            logging.getLogger("notionary.base_notion_client"),
            logging.getLogger("notionary.page"),
            logging.getLogger("notionary.database"),
            # Also suppress the root logger if needed
            logging.getLogger(),
        ]

        # Store original levels and set to CRITICAL to suppress ERROR logs
        original_levels = {}
        for logger in loggers_to_suppress:
            original_levels[logger] = logger.level
            logger.setLevel(logging.CRITICAL)

        try:
            yield
        finally:
            # Restore original log levels
            for logger, original_level in original_levels.items():
                logger.setLevel(original_level)

    async def _resolve_page_id(self, name: str) -> Optional[str]:
        """Search for pages matching the name."""
        search_results = await self.workspace.search_pages(
            query=name, limit=self.search_limit
        )

        return self._find_best_fuzzy_match(query=name, candidate_objects=search_results)

    async def _resolve_database_id(self, name: str) -> Optional[str]:
        """Search for databases matching the name."""
        search_results = await self.workspace.search_databases(
            query=name, limit=self.search_limit
        )

        return self._find_best_fuzzy_match(query=name, candidate_objects=search_results)

    def _find_best_fuzzy_match(
        self, query: str, candidate_objects: list
    ) -> Optional[str]:
        """
        Find the best fuzzy match among candidate objects using existing fuzzy matching logic.

        Args:
            query: The search query to match against
            candidate_objects: Objects (pages or databases) with .id and .title attributes

        Returns:
            ID of best match, or None if no match meets threshold
        """
        if not candidate_objects:
            return None

        # Use existing fuzzy matching logic
        best_match = find_best_match(
            query=query,
            items=candidate_objects,
            text_extractor=lambda obj: obj.title,
        )

        return best_match.item.id if best_match else None
