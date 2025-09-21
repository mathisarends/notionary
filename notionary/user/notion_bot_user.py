from __future__ import annotations

from notionary.user.base_notion_user import BaseNotionUser
from notionary.user.models import NotionBotUserResponse, WorkspaceLimits
from notionary.user.user_http_client import UserHttpClient
from notionary.util import factory_only
from notionary.util.fuzzy import find_best_match


class NotionBotUser(BaseNotionUser):
    """
    Manager for Notion bot users.
    Handles bot-specific operations and workspace information.
    """

    NO_USERS_FOUND_MSG = "No users found in workspace"
    NO_BOT_USERS_FOUND_MSG = "No bot users found in workspace"

    @factory_only("from_current_integration", "from_bot_response", "from_name")
    def __init__(
        self,
        user_id: str,
        name: str | None = None,
        avatar_url: str | None = None,
        workspace_name: str | None = None,
        workspace_limits: WorkspaceLimits | None = None,
        owner_type: str | None = None,
        token: str | None = None,
    ):
        """Initialize bot user with bot-specific properties."""
        super().__init__(user_id, name, avatar_url, token)
        self._workspace_name = workspace_name
        self._workspace_limits = workspace_limits
        self._owner_type = owner_type

    @classmethod
    async def from_current_integration(cls, token: str | None = None) -> NotionBotUser | None:
        """
        Get the current bot user (from the API token).

        Args:
            token: Optional Notion API token

        Returns:
            Optional[NotionBotUser]: Bot user instance or None if failed
        """
        client = UserHttpClient(token=token)
        bot_response = await client.get_bot_user()

        if bot_response is None:
            cls.logger.error("Failed to load bot user data")
            return None

        return cls._create_from_response(bot_response, token)

    @classmethod
    async def from_name(cls, name: str, token: str | None = None, min_similarity: float = 0.6) -> NotionBotUser | None:
        """
        Create a NotionBotUser by finding a bot user with fuzzy matching on the name.
        Uses Notion's list users API and fuzzy matching to find the best result.
        """
        client = UserHttpClient(token=token)

        try:
            # Get all users from workspace
            all_users_response = await client.get_all_users()

            if not all_users_response:
                cls.logger.warning(cls.NO_USERS_FOUND_MSG)
                raise ValueError(cls.NO_USERS_FOUND_MSG)

            # Filter to only bot users
            bot_users = [user for user in all_users_response if user.type == "bot" and user.name]

            if not bot_users:
                cls.logger.warning(cls.NO_BOT_USERS_FOUND_MSG)
                raise ValueError(cls.NO_BOT_USERS_FOUND_MSG)

            cls.logger.debug(
                "Found %d bot users for fuzzy matching: %s",
                len(bot_users),
                [user.name for user in bot_users[:5]],  # Log first 5 names
            )

            # Use fuzzy matching to find best match
            best_match = find_best_match(
                query=name,
                items=bot_users,
                text_extractor=lambda user: user.name or "",
                min_similarity=min_similarity,
            )

            if not best_match:
                available_names = [user.name for user in bot_users[:5]]
                cls.logger.warning(
                    "No sufficiently similar bot user found for '%s' (min: %.3f). Available: %s",
                    name,
                    min_similarity,
                    available_names,
                )
                raise ValueError(f"No sufficiently similar bot user found for '{name}'")

            cls.logger.info(
                "Found best match: '%s' with similarity %.3f for query '%s'",
                best_match.matched_text,
                best_match.similarity,
                name,
            )

            # Create NotionBotUser from the matched user response
            return cls._create_from_response(best_match.item, token)

        except Exception as e:
            cls.logger.error("Error finding bot user by name '%s': %s", name, str(e))
            raise

    @classmethod
    def from_bot_response(cls, bot_response: NotionBotUserResponse, token: str | None = None) -> NotionBotUser:
        """
        Create a NotionBotUser from an existing bot API response.

        Args:
            bot_response: Bot user response from Notion API
            token: Optional Notion API token

        Returns:
            NotionBotUser: Bot user instance
        """
        return cls._create_from_response(bot_response, token)

    @property
    def workspace_name(self) -> str | None:
        """Get the workspace name."""
        return self._workspace_name

    @property
    def workspace_limits(self) -> WorkspaceLimits | None:
        """Get the workspace limits."""
        return self._workspace_limits

    @property
    def owner_type(self) -> str | None:
        """Get the owner type ('workspace' or 'user')."""
        return self._owner_type

    @property
    def user_type(self) -> str:
        """Get the user type."""
        return "bot"

    @property
    def is_person(self) -> bool:
        """Check if this is a person user."""
        return False

    @property
    def is_bot(self) -> bool:
        """Check if this is a bot user."""
        return True

    @property
    def is_workspace_integration(self) -> bool:
        """Check if this is a workspace-owned integration."""
        return self._owner_type == "workspace"

    @property
    def is_user_integration(self) -> bool:
        """Check if this is a user-owned integration."""
        return self._owner_type == "user"

    @property
    def max_file_upload_size(self) -> int | None:
        """The maximum file upload size in bytes."""
        return self._workspace_limits.max_file_upload_size_in_bytes if self._workspace_limits else None

    def __str__(self) -> str:
        """String representation of the bot user."""
        workspace = self._workspace_name or "Unknown Workspace"
        return f"NotionBotUser(name='{self.get_display_name()}', workspace='{workspace}', id='{self._user_id[:8]}...')"

    @classmethod
    def _create_from_response(cls, bot_response: NotionBotUserResponse, token: str | None) -> NotionBotUser:
        """Create NotionBotUser instance from API response."""
        workspace_name = None
        workspace_limits = None
        owner_type = None

        if bot_response.bot:
            workspace_name = bot_response.bot.workspace_name
            workspace_limits = bot_response.bot.workspace_limits
            owner_type = bot_response.bot.owner.type if bot_response.bot.owner else None

        instance = cls(
            user_id=bot_response.id,
            name=bot_response.name,
            avatar_url=bot_response.avatar_url,
            workspace_name=workspace_name,
            workspace_limits=workspace_limits,
            owner_type=owner_type,
            token=token,
        )

        cls.logger.info(
            "Created bot user: '%s' (ID: %s, Workspace: %s)",
            bot_response.name or "Unknown Bot",
            bot_response.id,
            workspace_name or "Unknown",
        )

        return instance
