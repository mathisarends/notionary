from typing import Any, Dict, List, Optional

from notionary.user.client import NotionUserClient
from notionary.user.models import NotionUsersListResponse
from notionary.user.notion_user import NotionUser
from notionary.util import LoggingMixin


class NotionUserManager(LoggingMixin):
    """
    Manager for user operations within API limitations.

    Note: The Notion API provides endpoints to list workspace users (excluding guests).
    This manager provides utility functions for working with individual users and user lists.
    """

    def __init__(self, token: Optional[str] = None):
        """Initialize the user manager."""
        self.client = NotionUserClient(token=token)

    async def get_current_bot_user(self) -> Optional[NotionUser]:
        """
        Get the current bot user from the API token.
        """
        return await NotionUser.current_bot_user(token=self.client.token)

    async def get_user_by_id(self, user_id: str) -> Optional[NotionUser]:
        """
        Get a specific user by their ID.
        """
        return await NotionUser.from_user_id(user_id, token=self.client.token)

    async def list_users(
        self, page_size: int = 100, start_cursor: Optional[str] = None
    ) -> Optional[NotionUsersListResponse]:
        """
        List users in the workspace (paginated).

        Note: Guests are not included in the response.
        """
        try:
            response = await self.client.list_users(page_size, start_cursor)
            if response is None:
                self.logger.error("Failed to list users")
                return None

            self.logger.info(
                "Retrieved %d users (has_more: %s)",
                len(response.results),
                response.has_more,
            )
            return response

        except Exception as e:
            self.logger.error("Error listing users: %s", str(e))
            return None

    async def get_all_users(self) -> List[NotionUser]:
        """
        Get all users in the workspace as NotionUser objects.
        Automatically handles pagination and converts responses to NotionUser instances.
        """
        try:
            # Get raw user responses
            user_responses = await self.client.get_all_users()

            # Convert to NotionUser objects
            notion_users = []
            for user_response in user_responses:
                try:
                    # Use the internal creation method to convert response to NotionUser
                    notion_user = NotionUser.from_notion_user_response(
                        user_response, self.client.token
                    )
                    notion_users.append(notion_user)
                except Exception as e:
                    self.logger.warning(
                        "Failed to convert user %s to NotionUser: %s",
                        user_response.id,
                        str(e),
                    )
                    continue

            self.logger.info(
                "Successfully converted %d users to NotionUser objects",
                len(notion_users),
            )
            return notion_users

        except Exception as e:
            self.logger.error("Error getting all users: %s", str(e))
            return []

    async def get_users_by_type(self, user_type: str = "person") -> List[NotionUser]:
        """
        Get all users of a specific type (person or bot).
        """
        try:
            all_users = await self.get_all_users()
            filtered_users = [user for user in all_users if user.user_type == user_type]

            self.logger.info(
                "Found %d users of type '%s' out of %d total users",
                len(filtered_users),
                user_type,
                len(all_users),
            )
            return filtered_users

        except Exception as e:
            self.logger.error("Error filtering users by type: %s", str(e))
            return []

    # TODO: Type this
    async def get_workspace_info(self) -> Optional[Dict[str, Any]]:
        """
        Get available workspace information from the bot user.
        """
        bot_user = await self.get_current_bot_user()
        if bot_user is None:
            self.logger.error("Failed to get bot user for workspace info")
            return None

        workspace_info = {
            "workspace_name": bot_user.workspace_name,
            "bot_user_id": bot_user.id,
            "bot_user_name": bot_user.name,
            "bot_user_type": bot_user.user_type,
        }

        # Add workspace limits if available
        if bot_user.is_bot:
            limits = await bot_user.get_workspace_limits()
            if limits:
                workspace_info["workspace_limits"] = limits

        # Add user count statistics
        try:
            all_users = await self.get_all_users()
            workspace_info["total_users"] = len(all_users)
            workspace_info["person_users"] = len([u for u in all_users if u.is_person])
            workspace_info["bot_users"] = len([u for u in all_users if u.is_bot])
        except Exception as e:
            self.logger.warning("Could not get user statistics: %s", str(e))

        return workspace_info

    async def find_users_by_name(self, name_pattern: str) -> List[NotionUser]:
        """
        Find users by name pattern (case-insensitive partial match).

        Note: The API doesn't support server-side filtering, so this fetches all users
        and filters client-side.
        """
        try:
            all_users = await self.get_all_users()
            pattern_lower = name_pattern.lower()

            matching_users = [
                user
                for user in all_users
                if user.name and pattern_lower in user.name.lower()
            ]

            self.logger.info(
                "Found %d users matching pattern '%s'",
                len(matching_users),
                name_pattern,
            )
            return matching_users

        except Exception as e:
            self.logger.error("Error finding users by name: %s", str(e))
            return []
