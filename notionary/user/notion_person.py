from dataclasses import dataclass

from notionary.user.user_http_client import UserHttpClient
from notionary.user.user_models import NotionPersonResponse, UserType
from notionary.util.fuzzy import find_best_match


@dataclass
class NotionPerson:
    id: str
    name: str
    avatar_url: str
    email: str


class NotionPersonFactory:
    def __init__(self, http_client: UserHttpClient | None = None) -> None:
        self.http_client = http_client or UserHttpClient()

    async def from_name(self, name: str) -> NotionPerson:
        all_users = await self._get_all_persons()

        if not all_users:
            raise ValueError("No person users found in the workspace")

        best_match = find_best_match(query=name, items=all_users, text_extractor=lambda user: user.name or "")
        if not best_match:
            raise ValueError(f"No person user found with name similar to '{name}'")

        return best_match

    async def _get_all_persons(self) -> list[NotionPerson]:
        workspace_entities = await self.http_client.get_all_workspace_users()

        persons = [entity for entity in workspace_entities if entity.type == UserType.PERSON]
        return [self._from_response(response) for response in persons]

    async def from_user_id(self, user_id: str) -> NotionPerson:
        user_response = await self.http_client.get_user_by_id(user_id)

        if user_response.type != UserType.PERSON:
            raise ValueError(f"User {user_id} is not a person user, but {user_response.type}")

        return self._from_response(user_response)

    def _from_response(self, user_response: NotionPersonResponse) -> NotionPerson:
        return NotionPerson(
            id=user_response.id,
            name=user_response.name or "",
            avatar_url=user_response.avatar_url,
            email=user_response.person.email,
        )
