from typing import override

from notionary.blocks.rich_text.name_id_resolver.name_id_resolver import NameIdResolver
from notionary.user.factories import PersonUserFactory
from notionary.utils.uuid_utils import _is_valid_uuid


class PersonNameIdResolver(NameIdResolver):
    def __init__(self, person_user_factory: PersonUserFactory | None = None) -> None:
        self.person_user_factory = person_user_factory or PersonUserFactory()

    @override
    async def resolve_name_to_id(self, name: str | None) -> str | None:
        """Resolve a user name or UUID to a user ID.

        Args:
            name: Either a user name or a valid UUID string

        Returns:
            User ID if found, None otherwise
        """
        if not name or not name.strip():
            return None

        name = name.strip()

        # Check if the input is already a UUID
        if _is_valid_uuid(name):
            try:
                user = await self.person_user_factory.from_user_id(name)
                return user.id if user else None
            except Exception:
                return None

        # Otherwise treat it as a name
        try:
            user = await self.person_user_factory.from_name(name)
            return user.id if user else None
        except Exception:
            return None

    @override
    async def resolve_id_to_name(self, user_id: str | None) -> str | None:
        """Resolve a user ID to a user name.

        Args:
            user_id: A valid UUID string

        Returns:
            User name if found, None otherwise
        """
        if not user_id or not user_id.strip():
            return None

        try:
            user = await self.person_user_factory.from_user_id(user_id.strip())
            return user.name if user else None
        except Exception:
            return None
