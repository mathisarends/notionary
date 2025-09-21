from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.blocks.rich_text.name_id_resolvcer.base_name_id_resolver import BaseNameIdResolver
from notionary.util import format_uuid
from notionary.util.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionPage


class PageNameIdResolver(BaseNameIdResolver):
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

    async def _resolve_page_id(self, name: str) -> str | None:
        search_results = await self.workspace.search_pages(query=name, limit=self.search_limit)

        return self._find_best_fuzzy_match(query=name, candidate_objects=search_results)

    def _find_best_fuzzy_match(self, query: str, candidate_objects: list[NotionPage]) -> str | None:
        if not candidate_objects:
            return None

        best_match = find_best_match(
            query=query,
            items=candidate_objects,
            text_extractor=lambda obj: obj.title,
        )

        return best_match.item.id if best_match else None
