from pydantic import TypeAdapter

from notionary.http.client import HttpClient
from notionary.user.schemas import (
    BotUserResponseDto,
    UserResponseDto,
    UsersListResponseDto,
)
from notionary.utils.pagination import paginate_notion_api


class UserHttpClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get_user_by_id(self, user_id: str) -> UserResponseDto:
        response = await self._http.get(f"users/{user_id}")
        return TypeAdapter(UserResponseDto).validate_python(response)

    async def get_all_workspace_users(self) -> list[UserResponseDto]:
        return await paginate_notion_api(self._get_workspace_users, page_size=100)

    async def _get_workspace_users(
        self, page_size: int = 100, start_cursor: str | None = None
    ) -> UsersListResponseDto:
        params: dict = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self._http.get("users", params=params)
        return UsersListResponseDto.model_validate(response)

    async def get_current_integration_bot(self) -> BotUserResponseDto:
        response = await self._http.get("users/me")
        return BotUserResponseDto.model_validate(response)
