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
            case None:
                return [
                    mapper.to_person(u)
                    if u.type == UserType.PERSON
                    else mapper.to_bot(u)
                    for u in users
                ]

    @overload
    async def search(
        self, query: str, *, filter: Literal["person"]
    ) -> list[Person]: ...
    @overload
    async def search(self, query: str, *, filter: Literal["bot"]) -> list[Bot]: ...
    @overload
    async def search(self, query: str, *, filter: None = None) -> list[User]: ...

    async def search(
        self, query: str, *, filter: Literal["person", "bot"] | None = None
    ) -> list[Person] | list[Bot] | list[User]:
        query_lower = query.lower()
        users = await self.list(filter=filter)
        return [
            u
            for u in users
            if query_lower in (u.name or "").lower()
            or (isinstance(u, Person) and query_lower in u.email.lower())
        ]

    async def me(self) -> Bot:
        """Return the bot user associated with the current API token.

        Returns:
            The authenticated integration bot, including workspace metadata.
        """
        dto = await self._client.me()
        return mapper.to_bot(dto)
