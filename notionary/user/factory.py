from notionary.user.base import BaseUser
from notionary.user.bot import BotUser
from notionary.user.client import UserHttpClient
from notionary.user.person import PersonUser
from notionary.user.schemas import UserType


async def create_user_from_id(
    user_id: str,
    http_client: UserHttpClient | None = None,
) -> BaseUser:
    client = http_client or UserHttpClient()

    user_dto = await client.get_user_by_id(user_id)

    if user_dto.type == UserType.PERSON:
        return PersonUser.from_dto(user_dto)

    if user_dto.type == UserType.BOT:
        return BotUser.from_dto(user_dto)

    raise ValueError(f"User for id {user_id} could not been created.")
