from __future__ import annotations

from typing import Literal, overload

from notionary.http import HttpClient
from notionary.user import mapper
from notionary.user.client import UserClient
from notionary.user.models import Bot, Person, User
from notionary.user.schemas import UserType


class UsersNamespace:
    """Scoped access to Notion workspace users.

    Wraps the Notion Users API and maps raw responses to typed
    :class:`~notionary.user.models.Person` and
    :class:`~notionary.user.models.Bot` objects.
    """

    def __init__(self, http: HttpClient) -> None:
        self._client = UserClient(http)

    @overload
    async def list(self, *, filter: Literal["person"]) -> list[Person]: ...
    @overload
    async def list(self, *, filter: Literal["bot"]) -> list[Bot]: ...
    @overload
    async def list(self, *, filter: None = None) -> list[User]: ...

    async def list(
        self, *, filter: Literal["person", "bot"] | None = None
    ) -> list[Person] | list[Bot] | list[User]:
        """Return workspace members, optionally filtered by type.

        Args:
            filter: ``"person"`` for humans only, ``"bot"`` for integrations only,
                    ``None`` (default) for all members.

        Returns:
            A list of :class:`~notionary.user.models.Person`,
            :class:`~notionary.user.models.Bot`, or both.
        """
        users = await self._client.list()
        match filter:
            case "person":
                return [mapper.to_person(u) for u in users if u.type == UserType.PERSON]
            case "bot":
                return [mapper.to_bot(u) for u in users if u.type == UserType.BOT]

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
