from pydantic import TypeAdapter

from notionary.http.client import NotionHttpClient
from notionary.user.schemas import (
    BotUserResponseDto,
    NotionUsersListResponse,
    UserResponseDto,
)
from notionary.utils.pagination import paginate_notion_api


class UserHttpClient(NotionHttpClient):
    async def get_user_by_id(self, user_id: str) -> UserResponseDto | None:
        response = await self.get(f"users/{user_id}")

        adapter = TypeAdapter(UserResponseDto)
        return adapter.validate_python(response)

    async def get_all_workspace_users(self) -> list[UserResponseDto]:
        all_entities = await paginate_notion_api(self._get_workspace_entities, page_size=100)

        self.logger.info("Fetched %d total workspace users", len(all_entities))
        return all_entities

    async def _get_workspace_entities(
        self, page_size: int = 100, start_cursor: str | None = None
    ) -> NotionUsersListResponse | None:
        params = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self.get("users", params=params)

        return NotionUsersListResponse.model_validate(response)

    async def get_current_integration_bot(self) -> BotUserResponseDto:
        response = await self.get("users/me")

        return BotUserResponseDto.model_validate(response)
