from __future__ import annotations

from collections.abc import AsyncIterator

from notionary.user import BotUser, PersonUser
from notionary.user.client import UserHttpClient
from notionary.user.schemas import UserType


class UserService:
    def __init__(self, client: UserHttpClient | None = None) -> None:
        self._client = client or UserHttpClient()

    async def list_users(self) -> list[PersonUser]:
        all_users = await self._client.get_all_workspace_users()
        person_users = [user for user in all_users if user.type == UserType.PERSON]

        return [PersonUser.from_dto(user) for user in person_users]

    async def list_users_stream(self) -> AsyncIterator[PersonUser]:
        all_users = await self._client.get_all_workspace_users()
        for user in all_users:
            if user.type == UserType.PERSON:
                yield PersonUser.from_dto(user)

    async def list_bot_users(self) -> list[BotUser]:
        all_users = await self._client.get_all_workspace_users()
        bot_users = [user for user in all_users if user.type == UserType.BOT]

        return [BotUser.from_dto(user) for user in bot_users]

    async def list_bot_users_stream(self) -> AsyncIterator[BotUser]:
        all_users = await self._client.get_all_workspace_users()
        for user in all_users:
            if user.type == UserType.BOT:
                yield BotUser.from_dto(user)

    async def search_users(self, query: str) -> list[PersonUser]:
        all_person_users = await self.list_users()
        query_lower = query.lower()

        return [
            user
            for user in all_person_users
            if query_lower in (user.name or "").lower() or query_lower in (user.email or "").lower()
        ]

    async def search_users_stream(self, query: str) -> AsyncIterator[PersonUser]:
        query_lower = query.lower()

        async for user in self.list_users_stream():
            if query_lower in (user.name or "").lower() or query_lower in (user.email or "").lower():
                yield user

    async def get_current_bot(self) -> BotUser:
        bot_dto = await self._client.get_current_integration_bot()
        return BotUser.from_dto(bot_dto)

    async def get_user_by_id(self, user_id: str) -> PersonUser | BotUser | None:
        user_dto = await self._client.get_user_by_id(user_id)

        if user_dto.type == UserType.PERSON:
            return PersonUser.from_dto(user_dto)
        else:
            return BotUser.from_dto(user_dto)
