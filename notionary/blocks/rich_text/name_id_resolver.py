from __future__ import annotations

from notionary.user.notion_user_manager import NotionUserManager
from notionary.util import format_uuid
from notionary.util.fuzzy import find_best_match


class NameIdResolver:
    def __init__(
        self,
        *,
        token: str | None = None,
        search_limit: int = 10,
    ):
        from notionary import NotionWorkspace

        self.workspace = NotionWorkspace()
        self.notion_user_manager = NotionUserManager()
        self.search_limit = search_limit

    async def resolve_page_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()

        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        return await self._resolve_page_id(cleaned_name)

    async def resolve_page_name(self, page_id: str) -> str | None:
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

    async def resolve_database_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()

        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        return await self._resolve_database_id(cleaned_name)

    async def resolve_database_name(self, database_id: str) -> str | None:
        if not database_id:
            return None

        formatted_id = format_uuid(database_id)
        if not formatted_id:
            return None

        try:
            from notionary import NotionDatabase

            database = await NotionDatabase.from_database_id(formatted_id)
            return database.title if database else None
        except Exception:
            return None

    async def resolve_user_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()

        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        return await self._resolve_user_id(cleaned_name)

    async def resolve_user_name(self, user_id: str) -> str | None:
        if not user_id:
            return None

        formatted_id = format_uuid(user_id)
        if not formatted_id:
            return None

        try:
            user = await self.notion_user_manager.get_user_by_id(formatted_id)
            return user.name if user else None
        except Exception:
            return None

    async def _resolve_user_id(self, name: str) -> str | None:
        try:
            users = await self.notion_user_manager.find_users_by_name(name)

            if not users:
                return None

            best_match = find_best_match(
                query=name,
                items=users,
                text_extractor=lambda user: user.name or "",
            )

            return best_match.item.id if best_match else None
        except Exception:
            return None

    async def _resolve_page_id(self, name: str) -> str | None:
        search_results = await self.workspace.search_pages(query=name, limit=self.search_limit)

        return self._find_best_fuzzy_match(query=name, candidate_objects=search_results)

    async def _resolve_database_id(self, name: str) -> str | None:
        search_results = await self.workspace.search_databases(query=name, limit=self.search_limit)

        return self._find_best_fuzzy_match(query=name, candidate_objects=search_results)

    def _find_best_fuzzy_match(self, query: str, candidate_objects: list) -> str | None:
        if not candidate_objects:
            return None

        # Use existing fuzzy matching logic
        best_match = find_best_match(
            query=query,
            items=candidate_objects,
            text_extractor=lambda obj: obj.title,
        )

        return best_match.item.id if best_match else None
