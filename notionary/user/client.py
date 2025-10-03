from pydantic import TypeAdapter

from notionary.http.client import NotionHttpClient
from notionary.user.schemas import (
    NotionUsersListResponse,
    UserResponseDto,
)


class UserHttpClient(NotionHttpClient):
    async def get_user_by_id(self, user_id: str) -> UserResponseDto | None:
        response = await self.get(f"users/{user_id}")

        adapter = TypeAdapter(UserResponseDto)
        return adapter.validate_python(response)

    async def get_all_workspace_users(self) -> list[UserResponseDto]:
        all_entities = []
        start_cursor = None
        page_count = 0

        while True:
            response = await self._get_workspace_entities(page_size=100, start_cursor=start_cursor)

            page_count += 1
            all_entities.extend(response.results)

            self.logger.debug(
                "Fetched page %d: %d entities (total: %d)", page_count, len(response.results), len(all_entities)
            )

            if not response.has_more:
                self.logger.debug("No more pages - pagination complete")
                break

            start_cursor = response.next_cursor

            if start_cursor is None:
                self.logger.warning("has_more is True but next_cursor is None - stopping pagination")
                break

        self.logger.info(
            "Pagination complete: fetched %d total entities across %d pages", len(all_entities), page_count
        )
        return all_entities

    async def _get_workspace_entities(
        self, page_size: int = 100, start_cursor: str | None = None
    ) -> NotionUsersListResponse | None:
        params = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self.get("users", params=params)

        return NotionUsersListResponse.model_validate(response)
