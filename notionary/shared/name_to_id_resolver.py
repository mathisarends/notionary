from __future__ import annotations

from typing import Optional

from notionary.user.notion_user_manager import NotionUserManager
from notionary.util import format_uuid
from notionary.util.fuzzy import find_best_match


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
        self.notion_user_manager = NotionUserManager(token=token)
        self.search_limit = search_limit

    async def resolve_page_id(self, name: str) -> Optional[str]:
        """
        Convert a page name to its Notion page ID.
        Specifically searches only pages, not databases.
        """
        if not name:
            return None

        cleaned_name = name.strip()

        # Return if already a valid Notion ID
        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        # Search for page by name
        return await self._resolve_page_id(cleaned_name)

    async def resolve_database_id(self, name: str) -> Optional[str]:
        """
        Convert a database name to its Notion database ID.
        Specifically searches only databases, not pages.
        """
        if not name:
            return None

        cleaned_name = name.strip()

        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        return await self._resolve_database_id(cleaned_name)

    async def resolve_page_name(self, page_id: str) -> Optional[str]:
        """
        Convert a Notion page ID to its human-readable title.
        """
        if not page_id:
            return None

        formatted_id = format_uuid(page_id)
        if not formatted_id:
            return None

        try:
            from notionary import NotionPage

            page = await NotionPage.from_page_id(formatted_id)
            return page.title if page else None
        except Exception:
            return None

    async def resolve_database_name(self, database_id: str) -> Optional[str]:
        """
        Convert a Notion database ID to its human-readable title.
        """
        if not database_id:
            return None

        # Validate and format UUID
        formatted_id = format_uuid(database_id)
        if not formatted_id:
            return None

        try:
            from notionary import NotionDatabase

            database = await NotionDatabase.from_database_id(formatted_id)
            return database.title if database else None
        except Exception:
            return None

    async def resolve_user_id(self, name: str) -> Optional[str]:
        """
        Convert a user name to its Notion user ID.
        Specifically searches only users.
        """
        if not name:
            return None

        cleaned_name = name.strip()

        # Return if already a valid Notion ID
        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        # Search for user by name
        return await self._resolve_user_id(cleaned_name)

    async def resolve_user_name(self, user_id: str) -> Optional[str]:
        """
        Convert a Notion user ID to its human-readable name.

        Args:
            user_id: Notion user ID to resolve

        Returns:
            User name if found, None if not found or inaccessible
        """
        if not user_id:
            return None

        # Validate and format UUID
        formatted_id = format_uuid(user_id)
        if not formatted_id:
            return None

        try:
            user = await self.notion_user_manager.get_user_by_id(formatted_id)
            return user.name if user else None
        except Exception:
            return None

    async def _resolve_user_id(self, name: str) -> Optional[str]:
        """Search for users matching the name."""
        try:
            users = await self.notion_user_manager.find_users_by_name(name)

            if not users:
                return None

            # Use fuzzy matching to find best match
            best_match = find_best_match(
                query=name,
                items=users,
                text_extractor=lambda user: user.name or "",
            )

            return best_match.item.id if best_match else None
        except Exception:
            return None

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
