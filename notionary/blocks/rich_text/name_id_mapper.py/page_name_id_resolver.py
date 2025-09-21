from notionary.blocks.rich_text.name_id_resolver import NameIdResolver


class PageNameIdResolver(NameIdResolver):
    async def _search_entity_by_name(self, name: str) -> str | None:
        search_results = await self.workspace.search_pages(query=name, limit=self.search_limit)
        return self._find_best_fuzzy_match(query=name, candidate_objects=search_results)

    async def _resolve_formatted_id_to_name(self, formatted_id: str) -> str | None:
        try:
            from notionary import NotionPage

            page = await NotionPage.from_page_id(formatted_id)
            return page.title if page else None
        except Exception:
            return None
