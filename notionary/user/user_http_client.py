from notionary.http.notion_http_client import NotionHttpClient
from notionary.user.models import (
    NotionBotUserResponse,
    NotionUserResponse,
    NotionUsersListResponse,
)


class UserHttpClient(NotionHttpClient):
    """
    Client for Notion user-specific operations.
    Inherits base HTTP functionality from NotionHttpClient.

    Note: The Notion API only supports individual user queries and bot user info.
    List users endpoint is available but only returns workspace members (no guests).
    """

    async def get_user(self, user_id: str) -> NotionUserResponse | None:
        """
        Retrieve a user by their ID.
        """
        response = await self.get(f"users/{user_id}")
        if response is None:
            self.logger.error("Failed to fetch user %s - API returned None", user_id)
            return None

        try:
            return NotionUserResponse.model_validate(response)
        except Exception as e:
            self.logger.error("Failed to validate user response for %s: %s", user_id, e)
            return None

    async def get_bot_user(self) -> NotionBotUserResponse | None:
        """
        Retrieve your token's bot user information.
        """
        response = await self.get("users/me")
        if response is None:
            self.logger.error("Failed to fetch bot user - API returned None")
            return None

        try:
            return NotionBotUserResponse.model_validate(response)
        except Exception as e:
            self.logger.error("Failed to validate bot user response: %s", e)
            return None

    async def list_users(
        self, page_size: int = 100, start_cursor: str | None = None
    ) -> NotionUsersListResponse | None:
        """
        List all users in the workspace (paginated).

        Note: Guests are not included in the response.
        """
        params = {"page_size": min(page_size, 100)}  # API max is 100
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self.get("users", params=params)
        if response is None:
            self.logger.error("Failed to fetch users list - API returned None")
            return None

        try:
            return NotionUsersListResponse.model_validate(response)
        except Exception as e:
            self.logger.error("Failed to validate users list response: %s", e)
            return None

    async def get_all_users(self) -> list[NotionUserResponse]:
        """
        Get all users in the workspace by handling pagination automatically.
        """
        all_users = []
        start_cursor = None

        while True:
            try:
                response = await self.list_users(
                    page_size=100, start_cursor=start_cursor
                )

                if not response or not response.results:
                    break

                all_users.extend(response.results)

                # Check if there are more pages
                if not response.has_more or not response.next_cursor:
                    break

                start_cursor = response.next_cursor

            except Exception as e:
                self.logger.error("Error fetching all users: %s", str(e))
                break

        self.logger.info("Retrieved %d total users from workspace", len(all_users))
        return all_users

    async def get_workspace_name(self) -> str | None:
        """
        Get the workspace name from the bot user.
        """
        try:
            bot_user = await self.get_bot_user()
            if bot_user and bot_user.bot and bot_user.bot.workspace_name:
                return bot_user.bot.workspace_name
            return None
        except Exception as e:
            self.logger.error("Error fetching workspace name: %s", str(e))
            return None

    async def get_workspace_limits(self) -> dict | None:
        """
        Get workspace limits from the bot user.
        """
        try:
            bot_user = await self.get_bot_user()
            if bot_user and bot_user.bot and bot_user.bot.workspace_limits:
                return bot_user.bot.workspace_limits.model_dump()
            return None
        except Exception as e:
            self.logger.error("Error fetching workspace limits: %s", str(e))
            return None
