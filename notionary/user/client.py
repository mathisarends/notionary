from pydantic import TypeAdapter

from notionary.http.client import HttpClient
from notionary.user.schemas import (
    BotUserResponseDto,
    UserResponseDto,
)


class UserClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get(self, user_id: str) -> UserResponseDto:
        response = await self._http.get(f"users/{user_id}")
        return TypeAdapter(UserResponseDto).validate_python(response)

    async def list(self) -> list[UserResponseDto]:
        raw = await self._http.paginate("users", method="GET", page_size=100)
        adapter = TypeAdapter(UserResponseDto)
        return [adapter.validate_python(item) for item in raw]

    async def me(self) -> BotUserResponseDto:
        response = await self._http.get("users/me")
        return BotUserResponseDto.model_validate(response)
