from typing import override

from notionary.blocks.rich_text.name_id_resolver.name_id_resolver import NameIdResolver
from notionary.user.notion_user import NotionUser
from notionary.workspace.search.search_client import SearchClient


class UserNameIdResolver(NameIdResolver):
    def __init__(self, search_client: SearchClient | None = None) -> None:
        self._search_client = search_client or SearchClient()

    @override
    async def resolve_name_to_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()
        try:
            user = await self._search_client.find_user(cleaned_name)
            return user.id if user else None
        except Exception:
            return None

    @override
    async def resolve_id_to_name(self, user_id: str) -> str | None:
        if not user_id:
            return None

        try:
            user = await NotionUser.from_user_id(user_id)
            return user.name if user else None
        except Exception:
            return None
