from typing import Optional

from notionary.user.client import NotionUserClient
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

    async def get_user_by_id(self, user_id: str) -> Optional[NotionUser]:
        """
        Get a specific user by their ID.
        """
        return await NotionUser.from_user_id(user_id, token=self.client.token)

    async def get_all_users(self) -> list[NotionUser]:
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
                    notion_user = NotionUser.from_user_response(
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

    async def find_users_by_name(self, name_pattern: str) -> list[NotionUser]:
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
