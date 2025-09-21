from notionary.user.notion_user import NotionUser
from notionary.user.user_http_client import UserHttpClient
from notionary.util import LoggingMixin


class NotionUserManager(LoggingMixin):
    """
    Manager for user operations within API limitations.

    Note: The Notion API provides endpoints to list workspace users (excluding guests).
    This manager provides utility functions for working with individual users and user lists.
    """

    def __init__(self):
        """Initialize the user manager."""
        self.client = UserHttpClient()

    async def get_user_by_id(self, user_id: str) -> NotionUser | None:
        """
        Get a specific user by their ID.
        """
        return await NotionUser.from_user_id(user_id)

    async def get_all_users(self) -> list[NotionUser]:
        """
        Get all users in the workspace as NotionUser objects.
        Automatically handles pagination and converts responses to NotionUser instances.
        Only returns person users, excludes bots and integrations.
        """
        try:
            # Get raw user responses
            user_responses = await self.client.get_all_users()

            # Filter for person users only and convert to NotionUser objects
            notion_users = []
            for user_response in user_responses:
                # Skip bot users and integrations
                if user_response.type != "person":
                    self.logger.debug(
                        "Skipping non-person user %s (type: %s)",
                        user_response.id,
                        user_response.type,
                    )
                    continue

                try:
                    # Use the internal creation method to convert response to NotionUser
                    notion_user = NotionUser.from_user_response(user_response)
                    notion_users.append(notion_user)
                except Exception as e:
                    self.logger.warning(
                        "Failed to convert person user %s to NotionUser: %s",
                        user_response.id,
                        str(e),
                    )
                    continue

            self.logger.info(
                "Successfully converted %d person users to NotionUser objects (skipped %d non-person users)",
                len(notion_users),
                len(user_responses) - len(notion_users),
            )
            return notion_users

        except Exception as e:
            self.logger.error("Error getting all users: %s", str(e))
            return []

    async def find_users_by_name(self, name_pattern: str) -> list[NotionUser]:
        """
        Find person users by name pattern (case-insensitive partial match).
        Only returns person users, excludes bots and integrations.

        Note: The API doesn't support server-side filtering, so this fetches all users
        and filters client-side.
        """
        try:
            # get_all_users() already filters for person users only
            all_users = await self.get_all_users()
            pattern_lower = name_pattern.lower()

            matching_users = [user for user in all_users if user.name and pattern_lower in user.name.lower()]

            self.logger.info(
                "Found %d person users matching pattern '%s'",
                len(matching_users),
                name_pattern,
            )
            return matching_users

        except Exception as e:
            self.logger.error("Error finding users by name: %s", str(e))
            return []
