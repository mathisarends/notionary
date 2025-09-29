from dataclasses import dataclass

from notionary.user.user_http_client import UserHttpClient
from notionary.user.user_models import NotionBotResponse, UserType, WorkspaceOwnerType
from notionary.util.fuzzy import find_best_match


@dataclass
class NotionBotUser:
    id: str
    workspace_file_upload_limit_in_bytes: int
    owner_type: WorkspaceOwnerType
    name: str | None = None
    avatar_url: str | None = None
    workspace_name: str | None = None


class NotionBotFactory:
    def __init__(self, http_client: UserHttpClient | None = None) -> None:
        self.http_client = http_client or UserHttpClient()

    async def from_name(self, name: str) -> NotionBotUser:
        all_users = await self._get_all_bots()

        if not all_users:
            raise ValueError("No bot users found in the workspace")

        best_match = find_best_match(query=name, items=all_users, text_extractor=lambda user: user.name or "")
        if not best_match:
            raise ValueError(f"No bot user found with name similar to '{name}'")

        return best_match

    async def _get_all_bots(self) -> list[NotionBotUser]:
        workspace_entities = await self.http_client.get_all_workspace_users()
        bot_users = [entity for entity in workspace_entities if entity.type == UserType.BOT]

        return [self._from_response(response) for response in bot_users]

    async def from_id(self, user_id: str) -> NotionBotUser:
        user_response = await self.http_client.get_user_by_id(user_id)

        if user_response.type != UserType.BOT:
            raise ValueError(f"User {user_id} is not a bot user, but {user_response.type}")

        return self._from_response(user_response)

    def _from_response(self, user_response: NotionBotResponse) -> NotionBotUser:
        return NotionBotUser(
            id=user_response.id,
            name=user_response.name,
            avatar_url=user_response.avatar_url,
            workspace_name=user_response.bot.workspace_name,
            workspace_file_upload_limit_in_bytes=user_response.bot.workspace_limits.max_file_upload_size_in_bytes
            if user_response.bot.workspace_limits
            else 0,
            owner_type=user_response.bot.owner.type if user_response.bot.owner else None,
        )
