from __future__ import annotations

from notionary.blocks.rich_text.name_id_resolver.base_name_id_resolver import BaseNameIdResolver
from notionary.util import format_uuid
from notionary.util.fuzzy import find_best_match


class UserNameIdResolver(BaseNameIdResolver):
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
            user = await self.workspace.get_user_by_id(formatted_id)
            return user.name if user else None
        except Exception:
            return None

    async def _resolve_user_id(self, name: str) -> str | None:
        try:
            users = await self.workspace.search_users(name)

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
