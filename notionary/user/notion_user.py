from __future__ import annotations

from typing import Any, Dict, Optional
from notionary.user.client import NotionUserClient
from notionary.user.models import (
    NotionUserResponse,
)
from notionary.util import LoggingMixin, factory_only


class NotionUser(LoggingMixin):
    """
    Manager for individual Notion user operations and information.

    Note: Due to Notion API limitations, bulk user operations are not supported.
    Only individual user queries and bot user information are available.
    """

    @factory_only("from_user_id", "current_bot_user", "from_notion_user_response")
    def __init__(
        self,
        user_id: str,
        name: Optional[str] = None,
        user_type: Optional[str] = None,
        avatar_url: Optional[str] = None,
        email: Optional[str] = None,
        workspace_name: Optional[str] = None,
        is_bot: bool = False,
        token: Optional[str] = None,
    ):
        """
        Initialize the user manager with user metadata.
        """
        self._user_id = user_id
        self._name = name
        self._user_type = user_type
        self._avatar_url = avatar_url
        self._email = email
        self._workspace_name = workspace_name
        self._is_bot = is_bot

        self.client = NotionUserClient(token=token)

    @classmethod
    async def from_user_id(
        cls, user_id: str, token: Optional[str] = None
    ) -> Optional[NotionUser]:
        """
        Create a NotionUser from a user ID.

        Args:
            user_id: The ID of the Notion user
            token: Optional Notion API token

        Returns:
            Optional[NotionUser]: User manager instance or None if failed
        """
        async with NotionUserClient(token=token) as client:
            user_response = await client.get_user(user_id)
            if user_response is None:
                cls.logger.error(
                    "Failed to create NotionUser from user_id: %s", user_id
                )
                return None
            return cls._create_from_response(user_response, token)

    @classmethod
    async def current_bot_user(
        cls, token: Optional[str] = None
    ) -> Optional[NotionUser]:
        """
        Get the current bot user (from the API token).

        Args:
            token: Optional Notion API token

        Returns:
            Optional[NotionUser]: Bot user manager instance or None if failed
        """
        async with NotionUserClient(token=token) as client:
            bot_response = await client.get_bot_user()
            if bot_response is None:
                cls.logger.error("Failed to get current bot user")
                return None
            return cls._create_from_response(bot_response, token)

    @classmethod
    def from_notion_user_response(
        cls, user_response: NotionUserResponse, token: Optional[str] = None
    ) -> NotionUser:
        """
        Create a NotionUser from an existing API response.

        Args:
            user_response: User response from Notion API
            token: Optional Notion API token

        Returns:
            NotionUser: User manager instance
        """
        return cls._create_from_response(user_response, token)

    # ... rest of your existing methods remain the same ...

    @property
    def id(self) -> str:
        """Get the user ID (readonly)."""
        return self._user_id

    @property
    def name(self) -> Optional[str]:
        """Get the user name (readonly)."""
        return self._name

    @property
    def user_type(self) -> Optional[str]:
        """Get the user type ('person' or 'bot') (readonly)."""
        return self._user_type

    @property
    def avatar_url(self) -> Optional[str]:
        """Get the avatar URL (readonly)."""
        return self._avatar_url

    @property
    def email(self) -> Optional[str]:
        """Get the email (readonly, only for person users with proper capabilities)."""
        return self._email

    @property
    def workspace_name(self) -> Optional[str]:
        """Get the workspace name (readonly, only for bot users)."""
        return self._workspace_name

    @property
    def is_bot(self) -> bool:
        """Check if this is a bot user (readonly)."""
        return self._is_bot

    @property
    def is_person(self) -> bool:
        """Check if this is a person user (readonly)."""
        return not self._is_bot

    async def get_workspace_limits(self) -> Optional[Dict[str, Any]]:
        """
        Get workspace limits if this is a bot user.

        Returns:
            Optional[Dict[str, Any]]: Workspace limits or None
        """
        if not self._is_bot:
            self.logger.warning("Workspace limits only available for bot users")
            return None

        return await self.client.get_workspace_limits()

    async def refresh_user_data(self) -> bool:
        """
        Refresh user data from the Notion API.

        Returns:
            bool: True if refresh was successful
        """
        try:
            if self._is_bot:
                user_response = await self.client.get_bot_user()
            else:
                user_response = await self.client.get_user(self._user_id)

            if user_response is None:
                self.logger.error("Failed to refresh user data - API returned None")
                return False

            updated_user = self._create_from_response(user_response, self.client.token)

            # Update instance variables
            self._name = updated_user._name
            self._user_type = updated_user._user_type
            self._avatar_url = updated_user._avatar_url
            self._email = updated_user._email
            self._workspace_name = updated_user._workspace_name

            self.logger.info("Successfully refreshed user data for: %s", self._user_id)
            return True

        except Exception as e:
            self.logger.error("Error refreshing user data: %s", str(e))
            return False

    @classmethod
    def _create_from_response(
        cls, user_response: NotionUserResponse, token: Optional[str]
    ) -> NotionUser:
        """
        Create NotionUser instance from API response.
        """
        name = user_response.name
        user_type = user_response.type
        avatar_url = user_response.avatar_url

        # Extract email for person users
        email = None
        if user_response.person and user_response.person.email:
            email = user_response.person.email

        # Extract workspace info for bot users
        workspace_name = None
        is_bot = user_type == "bot"

        if user_response.bot and user_response.bot.workspace_name:
            workspace_name = user_response.bot.workspace_name

        instance = cls(
            user_id=user_response.id,
            name=name,
            user_type=user_type,
            avatar_url=avatar_url,
            email=email,
            workspace_name=workspace_name,
            is_bot=is_bot,
            token=token,
        )

        cls.logger.info(
            "Created user manager: '%s' (ID: %s, Type: %s)",
            name or "Unknown",
            user_response.id,
            user_type or "unknown",
        )

        return instance
