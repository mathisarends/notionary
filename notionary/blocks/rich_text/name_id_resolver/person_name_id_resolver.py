from typing import override

from notionary.blocks.rich_text.name_id_resolver.name_id_resolver import NameIdResolver
from notionary.user.client import UserHttpClient
from notionary.user.person import PersonUser


class PersonNameIdResolver(NameIdResolver):
    def __init__(self, http_client: UserHttpClient | None = None) -> None:
        self.http_client = http_client

    @override
    async def resolve_name_to_id(self, name: str | None) -> str | None:
        if not name or not name.strip():
            return None

        name = name.strip()

        try:
            user = await PersonUser.from_name(name, self.http_client)
            return user.id if user else None
        except Exception:
            return None

    @override
    async def resolve_id_to_name(self, user_id: str | None) -> str | None:
        if not user_id or not user_id.strip():
            return None

        try:
            user = await PersonUser.from_id(user_id.strip(), self.http_client)
            return user.name if user else None
        except Exception:
            return None
