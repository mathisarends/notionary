from __future__ import annotations

from typing import Optional

from notionary.user.client import NotionUserClient
from notionary.user.models import NotionBotUserResponse, WorkspaceLimits, WorkspaceInfo
from notionary.util import LoggingMixin, factory_only


class NotionIntegrationBot(LoggingMixin):
    """
    Represents the integration's bot user with convenient access to bot-specific information.

    This class provides a clean interface for working with the current integration's bot user,
    including workspace information, limits, and owner details.
    """

    @factory_only("from_token", "from_integration")
    def __init__(
        self,
        bot_user_data: NotionBotUserResponse,
        workspace_info: WorkspaceInfo,
        token: Optional[str] = None,
    ):
        """
        Initialize the integration bot manager with pre-loaded data.
        Use factory methods to create instances.
        """
        self._bot_user_data = bot_user_data
        self._workspace_info = workspace_info
        self._client = NotionUserClient(token=token)

    @classmethod
    async def from_token(cls, token: Optional[str] = None) -> NotionIntegrationBot:
        """
        Create a NotionIntegrationBot instance by loading data with the provided token.

        Args:
            token: Optional Notion API token (uses environment variable if not provided)

        Returns:
            NotionIntegrationBot: Configured bot instance with loaded data

        Raises:
            ValueError: If bot user data cannot be loaded
        """
        client = NotionUserClient(token=token)
        bot_user_data = await client.get_bot_user()

        if bot_user_data is None:
            cls.logger.error("Failed to load bot user data from API")
            raise ValueError("Unable to load bot user data from Notion API")

        workspace_info = cls._create_workspace_info(bot_user_data)

        instance = cls(
            bot_user_data=bot_user_data,
            workspace_info=workspace_info,
            token=token,
        )

        cls.logger.info(
            "Created integration bot: '%s' (ID: %s)",
            bot_user_data.name or "Unnamed Bot",
            bot_user_data.id,
        )

        return instance

    @classmethod
    async def from_integration(cls) -> NotionIntegrationBot:
        """
        Create a NotionIntegrationBot instance using the current environment token.

        Returns:
            NotionIntegrationBot: Configured bot instance with loaded data
        Raises:
            ValueError: If bot user data cannot be loaded
        """
        return await cls.from_token(token=None)

    @property
    def info(self) -> NotionBotUserResponse:
        """
        The complete bot user information.
        """
        return self._bot_user_data

    @property
    def id(self) -> str:
        """
        The bot user ID.
        """
        return self._bot_user_data.id

    @property
    def name(self) -> Optional[str]:
        """
        The bot user name.
        """
        return self._bot_user_data.name

    @property
    def workspace_info(self) -> WorkspaceInfo:
        """
        Comprehensive workspace information.
        """
        return self._workspace_info

    @property
    def workspace_name(self) -> Optional[str]:
        """
        The workspace name.
        """
        return self._workspace_info.name

    @property
    def workspace_limits(self) -> Optional[WorkspaceLimits]:
        """
        Workspace limits and restrictions.
        """
        return self._workspace_info.limits

    @property
    def max_file_upload_size(self) -> Optional[int]:
        """
        The maximum file upload size in bytes.
        """
        limits = self.workspace_limits
        return limits.max_file_upload_size_in_bytes if limits else None

    @property
    def is_workspace_integration(self) -> bool:
        """
        True if this is a workspace-owned integration.
        """
        return self._workspace_info.is_workspace_owned

    @property
    def is_user_integration(self) -> bool:
        """
        True if this is a user-owned integration.
        """
        return not self.is_workspace_integration

    @property
    def owner_type(self) -> Optional[str]:
        """
        The type of integration owner ("workspace" or "user").
        """
        return self._workspace_info.owner_type

    def __str__(self) -> str:
        """String representation of the bot."""
        name = self._bot_user_data.name or "Unnamed Bot"
        bot_id = self._bot_user_data.id[:8] + "..."
        workspace = self._workspace_info.name or "Unknown Workspace"
        return f"NotionIntegrationBot(name='{name}', id='{bot_id}', workspace='{workspace}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()

    @staticmethod
    def _create_workspace_info(bot_user_data: NotionBotUserResponse) -> WorkspaceInfo:
        """Create WorkspaceInfo from bot user data."""
        bot_data = bot_user_data.bot
        if not bot_data:
            return WorkspaceInfo()

        owner_type = bot_data.owner.type if bot_data.owner else None
        is_workspace_owned = owner_type == "workspace" if owner_type else False

        return WorkspaceInfo(
            name=bot_data.workspace_name,
            limits=bot_data.workspace_limits,
            owner_type=owner_type,
            is_workspace_owned=is_workspace_owned,
        )


async def main():
    """
    Example usage of the NotionIntegrationBot.
    """
    bot = await NotionIntegrationBot.from_integration()
    print(bot)
    print("Bot ID:", bot.id)
    print("Bot Name:", bot.name)
    print("Workspace Name:", bot.workspace_name)
    print("Max File Upload Size:", bot.max_file_upload_size, "bytes")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
