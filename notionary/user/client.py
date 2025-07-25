from typing import Optional
from notionary.base_notion_client import BaseNotionClient
from notionary.user.models import (
    NotionUserResponse,
    NotionBotUserResponse,
)
from notionary.util import singleton


@singleton
class NotionUserClient(BaseNotionClient):
    """
    Client for Notion user-specific operations.
    Inherits base HTTP functionality from BaseNotionClient.
    
    Note: The Notion API only supports individual user queries and bot user info.
    There is NO endpoint to list all workspace users via the standard API.
    """

    async def get_user(self, user_id: str) -> Optional[NotionUserResponse]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            Optional[NotionUserResponse]: The user object or None if failed
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

    async def get_bot_user(self) -> Optional[NotionBotUserResponse]:
        """
        Retrieve your token's bot user information.
        
        Returns:
            Optional[NotionBotUserResponse]: The bot user object with full details or None if failed
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

    async def get_workspace_name(self) -> Optional[str]:
        """
        Get the workspace name from the bot user.
        
        Returns:
            Optional[str]: Workspace name if available
        """
        try:
            bot_user = await self.get_bot_user()
            if bot_user and bot_user.bot and bot_user.bot.workspace_name:
                return bot_user.bot.workspace_name
            return None
        except Exception as e:
            self.logger.error("Error fetching workspace name: %s", str(e))
            return None

    async def get_workspace_limits(self) -> Optional[dict]:
        """
        Get workspace limits from the bot user.
        
        Returns:
            Optional[dict]: Workspace limits if available
        """
        try:
            bot_user = await self.get_bot_user()
            if bot_user and bot_user.bot and bot_user.bot.workspace_limits:
                return bot_user.bot.workspace_limits.model_dump()
            return None
        except Exception as e:
            self.logger.error("Error fetching workspace limits: %s", str(e))
            return None