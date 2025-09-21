from notionary.blocks.rich_text.name_id_resolver import NameIdResolver


class UserNameIdResolver(NameIdResolver):
    async def _search_entity_by_name(self, name: str) -> str | None:
        try:
            users = await self.workspace.search_users(query=name, limit=self.search_limit)
            if not users:
                return None

            best_match = self._find_best_fuzzy_match(
                query=name,
                items=users,
                text_extractor=lambda user: user.name,
            )
            return best_match.item.id if best_match else None
        except Exception:
            return None

    async def _resolve_formatted_id_to_name(self, formatted_id: str) -> str | None:
        try:
            user = await self.workspace.get_user_by_id(formatted_id)
            return user.name if user else None
        except Exception:
            return None
