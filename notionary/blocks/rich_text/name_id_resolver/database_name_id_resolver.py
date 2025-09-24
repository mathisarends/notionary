from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.blocks.rich_text.name_id_resolver.base_name_id_resolver import BaseNameIdResolver
from notionary.util.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionDatabase


class DatabaseNameIdResolver(BaseNameIdResolver):
    async def resolve_database_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()
        return await self._resolve_database_id(cleaned_name)

    async def resolve_database_name(self, database_id: str) -> str | None:
        if not database_id:
            return None

        try:
            from notionary import NotionDatabase

            database = await NotionDatabase.from_id(database_id)
            return database.title if database else None
        except Exception:
            return None

    async def _resolve_database_id(self, name: str) -> str | None:
        search_results = await self.workspace.search_databases(query=name, limit=self.search_limit)

        return self._find_best_fuzzy_match(query=name, candidate_objects=search_results)

    def _find_best_fuzzy_match(self, query: str, candidate_objects: list[NotionDatabase]) -> str | None:
        if not candidate_objects:
            return None

        best_match = find_best_match(
            query=query,
            items=candidate_objects,
            text_extractor=lambda obj: obj.title,
        )

        return best_match.item.id if best_match else None
