from typing import cast
from uuid import UUID

from notionary.http import HttpClient
from notionary.user.client import UserClient
from notionary.user.models import Bot, Person
from notionary.user.schemas import BotResponseDto, PersonResponseDto, UserType


class UsersNamespace:
    """Scoped access to Notion workspace users.

    Wraps the Notion Users API and maps raw responses to typed
    :class:`~notionary.user.models.Person` and
    :class:`~notionary.user.models.Bot` objects.
    """

    def __init__(self, http: HttpClient) -> None:
        self._client = UserClient(http)

    async def list_users(self) -> list[Person]:
        """Return all human workspace members.

        Returns:
            All users whose account type is ``person``.
        """
        users = await self._client.list()
        return [self._to_person(u) for u in users if u.type == UserType.PERSON]

    async def list_bots(self) -> list[Bot]:
        """Return all bot integrations in the workspace.

        Returns:
            All users whose account type is ``bot``.
        """
        users = await self._client.list()
        return [self._to_bot(u) for u in users if u.type == UserType.BOT]

    async def get(self, user_id: UUID) -> Person | Bot:
        """Fetch a single user by ID.

        Args:
            user_id: The Notion user UUID.

        Returns:
            :class:`~notionary.user.models.Person` or
            :class:`~notionary.user.models.Bot` depending on the account type.
        """
        dto = await self._client.get(user_id)
        if dto.type == UserType.PERSON:
            return self._to_person(dto)
        return self._to_bot(dto)

    async def me(self) -> Bot:
        """Return the bot user associated with the current API token.

        Returns:
            The authenticated integration bot, including workspace metadata.
        """
        dto = await self._client.me()
        return self._to_bot(dto)

    async def search(self, query: str) -> list[Person]:
        """Filter workspace members by name or email.

        Matching is case-insensitive and checks both fields.

        Args:
            query: Substring to match against name and email.

        Returns:
            All :class:`~notionary.user.models.Person` objects where
            ``query`` appears in ``name`` or ``email``.
        """
        query_lower = query.lower()
        return [
            u
            for u in await self.list_users()
            if query_lower in u.name.lower() or query_lower in u.email.lower()
        ]

    @staticmethod
    def _to_person(dto) -> Person:
        dto = cast(PersonResponseDto, dto)
        return Person(
            id=dto.id,
            name=dto.name or "",
            email=dto.email or "",
            avatar_url=dto.avatar_url,
        )

    @staticmethod
    def _to_bot(dto) -> Bot:
        dto = cast(BotResponseDto, dto)
        limit = (
            dto.bot.workspace_limits.max_file_upload_size_in_bytes
            if dto.bot.workspace_limits
            else 0
        )
        return Bot(
            id=dto.id,
            name=dto.name,
            workspace_name=dto.bot.workspace_name if dto.bot else None,
            workspace_file_upload_limit_in_bytes=limit,
            avatar_url=dto.avatar_url,
        )
