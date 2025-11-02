from typing import override

from notionary.shared.name_id_resolver.port import NameIdResolver
from notionary.workspace.query.service import WorkspaceQueryService


class PageNameIdResolver(NameIdResolver):
    def __init__(self, search_service: WorkspaceQueryService | None = None) -> None:
        self.search_service = search_service or WorkspaceQueryService()

    @override
    async def resolve_name_to_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()
        return await self._resolve_page_id(cleaned_name)

    @override
    async def resolve_id_to_name(self, page_id: str) -> str | None:
        if not page_id:
            return None

        try:
            from notionary import NotionPage

            page = await NotionPage.from_id(page_id)
            return page.title if page else None
        except Exception:
            return None

    async def _resolve_page_id(self, name: str) -> str | None:
        page = await self.search_service.find_page(query=name)
        return page.id if page else None
