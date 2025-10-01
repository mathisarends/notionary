from typing import cast

from notionary.user.client import UserHttpClient
from notionary.user.models import BotUser, PersonUser
from notionary.user.schemas import (
    BotUserResponseDto,
    PersonUserResponseDto,
    UserType,
)
from notionary.util.fuzzy import find_best_match


class BotUserFactory:
    def __init__(self, http_client: UserHttpClient | None = None) -> None:
        self.http_client = http_client or UserHttpClient()

    async def from_name(self, name: str) -> BotUser:
        all_bots = await self._get_all_bots()
        if not all_bots:
            raise ValueError("No 'bot' users found in the workspace")

        best_match = find_best_match(query=name, items=all_bots, text_extractor=lambda user: user.name or "")
        if not best_match:
            raise ValueError(f"No 'bot' user found with name similar to '{name}'")
        return best_match

    async def from_id(self, user_id: str) -> BotUser:
        user_dto = await self.http_client.get_user_by_id(user_id)

        if user_dto.type != UserType.BOT:
            raise ValueError(f"User {user_id} is not a 'bot', but '{user_dto.type.value}'")

        return self._from_dto(cast(BotUserResponseDto, user_dto))

    async def _get_all_bots(self) -> list[BotUser]:
        all_workspace_user_dtos = await self.http_client.get_all_workspace_users()

        bot_dtos = [dto for dto in all_workspace_user_dtos if dto.type == UserType.BOT]

        return [self._from_dto(cast(BotUserResponseDto, dto)) for dto in bot_dtos]

    def _from_dto(self, user_dto: BotUserResponseDto) -> BotUser:
        bot_dto = user_dto.bot
        owner_type = bot_dto.owner.type if bot_dto and bot_dto.owner else None
        workspace_name = bot_dto.workspace_name if bot_dto else None

        limit = 0
        if bot_dto and bot_dto.workspace_limits:
            limit = bot_dto.workspace_limits.max_file_upload_size_in_bytes

        return BotUser(
            id=user_dto.id,
            name=user_dto.name,
            avatar_url=user_dto.avatar_url,
            workspace_name=workspace_name,
            workspace_file_upload_limit_in_bytes=limit,
            owner_type=owner_type,
        )


class PersonUserFactory:
    def __init__(self, http_client: UserHttpClient | None = None) -> None:
        self.http_client = http_client or UserHttpClient()

    async def from_name(self, name: str) -> PersonUser:
        all_persons = await self._get_all_persons()
        if not all_persons:
            raise ValueError("No 'person' users found in the workspace")

        best_match = find_best_match(query=name, items=all_persons, text_extractor=lambda user: user.name or "")
        if not best_match:
            raise ValueError(f"No 'person' user found with name similar to '{name}'")
        return best_match

    async def from_id(self, user_id: str) -> PersonUser:
        user_dto = await self.http_client.get_user_by_id(user_id)

        if user_dto.type != UserType.PERSON:
            raise ValueError(f"User {user_id} is not a 'person', but '{user_dto.type.value}'")

        return self._from_dto(cast(PersonUserResponseDto, user_dto))

    async def _get_all_persons(self) -> list[PersonUser]:
        all_workspace_user_dtos = await self.http_client.get_all_workspace_users()

        person_dtos = [dto for dto in all_workspace_user_dtos if dto.type == UserType.PERSON]

        return [self._from_dto(cast(PersonUserResponseDto, dto)) for dto in person_dtos]

    def _from_dto(self, user_dto: PersonUserResponseDto) -> PersonUser:
        return PersonUser(
            id=user_dto.id,
            name=user_dto.name or "",
            avatar_url=user_dto.avatar_url,
            email=user_dto.person.email or "",
        )
