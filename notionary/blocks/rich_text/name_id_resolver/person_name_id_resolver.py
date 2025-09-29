from typing import override

from notionary.blocks.rich_text.name_id_resolver.name_id_resolver import NameIdResolver
from notionary.user.notion_person import NotionPersonFactory


class PersonNameIdResolver(NameIdResolver):
    def __init__(self, person_factory: NotionPersonFactory | None = None) -> None:
        self._person_factory = person_factory or NotionPersonFactory()

    @override
    async def resolve_name_to_id(self, name: str) -> str | None:
        if not name or not name.strip():
            return None

        try:
            user = await self._person_factory.from_name(name.strip())
            return user.id if user else None
        except Exception:
            return None

    @override
    async def resolve_id_to_name(self, user_id: str) -> str | None:
        if not user_id or not user_id.strip():
            return None

        try:
            user = await self._person_factory.from_user_id(user_id.strip())
            return user.name if user else None
        except Exception:
            return None
