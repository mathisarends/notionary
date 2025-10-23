from typing import Self, cast

from notionary.user.base import BaseUser
from notionary.user.client import UserHttpClient
from notionary.user.schemas import BotUserDto, BotUserResponseDto, UserResponseDto, UserType, WorkspaceOwnerType


class BotUser(BaseUser):
    def __init__(
        self,
        id: str,
        workspace_file_upload_limit_in_bytes: int,
        owner_type: WorkspaceOwnerType | None,
        name: str | None = None,
        avatar_url: str | None = None,
        workspace_name: str | None = None,
    ) -> None:
        super().__init__(id=id, name=name, avatar_url=avatar_url)
        self._workspace_name = workspace_name
        self._workspace_file_upload_limit_in_bytes = workspace_file_upload_limit_in_bytes
        self._owner_type = owner_type

    @property
    def workspace_name(self) -> str | None:
        return self._workspace_name

    @property
    def workspace_file_upload_limit_in_bytes(self) -> int:
        return self._workspace_file_upload_limit_in_bytes

    @property
    def owner_type(self) -> WorkspaceOwnerType | None:
        return self._owner_type

    @classmethod
    def _get_expected_user_type(cls) -> UserType:
        return UserType.BOT

    @classmethod
    async def from_current_integration(
        cls,
        http_client: UserHttpClient | None = None,
    ) -> Self:
        client = http_client or UserHttpClient()
        user_dto = await client.get_current_integration_bot()
        return cls.from_dto(user_dto)

    @classmethod
    def from_dto(cls, user_dto: UserResponseDto) -> Self:
        bot_dto = cast(BotUserResponseDto, user_dto)
        bot_data: BotUserDto = bot_dto.bot

        owner_type = bot_data.owner.type if bot_data and bot_data.owner else None
        workspace_name = bot_data.workspace_name if bot_data else None

        limit = 0
        if bot_data and bot_data.workspace_limits:
            limit = bot_data.workspace_limits.max_file_upload_size_in_bytes

        return cls(
            id=bot_dto.id,
            name=bot_dto.name,
            avatar_url=bot_dto.avatar_url,
            workspace_name=workspace_name,
            workspace_file_upload_limit_in_bytes=limit,
            owner_type=owner_type,
        )

    def __repr__(self) -> str:
        return f"BotUser(id={self._id!r}, name={self._name!r}, avatar_url={self._avatar_url!r}, workspace_name={self._workspace_name!r}, workspace_file_upload_limit_in_bytes={self._workspace_file_upload_limit_in_bytes!r}, owner_type={self._owner_type!r})"
