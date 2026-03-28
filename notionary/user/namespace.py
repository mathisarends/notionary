from typing import cast
from uuid import UUID

from notionary.http import HttpClient
from notionary.user.client import UserClient
from notionary.user.models import BotUser, PersonUser
from notionary.user.schemas import BotUserResponseDto, PersonUserResponseDto, UserType


class UsersNamespace:
    def __init__(self, http: HttpClient) -> None:
        self._client = UserClient(http)

    async def list_users(self) -> list[PersonUser]:
        users = await self._client.list()
        return [self._to_person(u) for u in users if u.type == UserType.PERSON]

    async def list_bots(self) -> list[BotUser]:
        users = await self._client.list()
        return [self._to_bot(u) for u in users if u.type == UserType.BOT]

    async def get(self, user_id: UUID) -> PersonUser | BotUser:
        dto = await self._client.get(user_id)
        if dto.type == UserType.PERSON:
            return self._to_person(dto)
        return self._to_bot(dto)

    async def me(self) -> BotUser:
        dto = await self._client.me()
        return self._to_bot(dto)

    async def search(self, query: str) -> list[PersonUser]:
        query_lower = query.lower()
        return [
            u
            for u in await self.list_users()
            if query_lower in u.name.lower() or query_lower in u.email.lower()
        ]

    @staticmethod
    def _to_person(dto) -> PersonUser:
        dto = cast(PersonUserResponseDto, dto)
        return PersonUser(
            id=dto.id,
            name=dto.name or "",
            email=dto.email or "",
            avatar_url=dto.avatar_url,
        )

    @staticmethod
    def _to_bot(dto) -> BotUser:
        dto = cast(BotUserResponseDto, dto)
        limit = (
            dto.bot.workspace_limits.max_file_upload_size_in_bytes
            if dto.bot.workspace_limits
            else 0
        )
        return BotUser(
            id=dto.id,
            name=dto.name,
            workspace_name=dto.bot.workspace_name if dto.bot else None,
            workspace_file_upload_limit_in_bytes=limit,
            avatar_url=dto.avatar_url,
        )
