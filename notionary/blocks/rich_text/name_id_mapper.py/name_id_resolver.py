from __future__ import annotations

from abc import ABC, abstractmethod

from notionary.util.fuzzy import find_best_match
from notionary.util.page_id_utils import format_uuid


class NameIdResolver(ABC):
    def __init__(self, *, search_limit: int = 10):
        from notionary import NotionWorkspace

        self.workspace = NotionWorkspace()
        self.search_limit = search_limit

    async def resolve_name_to_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()

        formatted_uuid = format_uuid(cleaned_name)
        if formatted_uuid:
            return formatted_uuid

        return await self._search_entity_by_name(cleaned_name)

    async def resolve_id_to_name(self, entity_id: str) -> str | None:
        if not entity_id:
            return None

        formatted_id = format_uuid(entity_id)
        if not formatted_id:
            return None

        return await self._resolve_formatted_id_to_name(formatted_id)

    @abstractmethod
    async def _search_entity_by_name(self, name: str) -> str | None:
        """Search for entities by name. Must be implemented by subclasses."""
        ...

    @abstractmethod
    async def _resolve_formatted_id_to_name(self, formatted_id: str) -> str | None:
        """Resolve a formatted ID to name. Must be implemented by subclasses."""
        ...

    def _find_best_fuzzy_match(self, query: str, candidate_objects: list) -> str | None:
        """Find the best fuzzy match from candidate objects."""
        if not candidate_objects:
            return None

        best_match = find_best_match(
            query=query,
            items=candidate_objects,
            text_extractor=lambda obj: obj.title,
        )

        return best_match.item.id if best_match else None
