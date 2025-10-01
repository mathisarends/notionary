from typing import override

from notionary.blocks.rich_text.name_id_resolver.name_id_resolver import NameIdResolver
from notionary.user.factories import PersonUserFactory


class PersonNameIdResolver(NameIdResolver):
    def __init__(self, person_user_factory: PersonUserFactory | None = None) -> None:
        self.person_user_factory = person_user_factory or PersonUserFactory()

    @override
    async def resolve_name_to_id(self, name: str) -> str | None:
        try:
            user = await self.person_user_factory.from_name(name)
            return user.id if user else None
        except Exception:
            return None

    @override
    async def resolve_id_to_name(self, user_id: str) -> str | None:
        try:
            user = await self.person_user_factory.from_id(user_id)
            return user.name if user else None
        except Exception:
            return None
