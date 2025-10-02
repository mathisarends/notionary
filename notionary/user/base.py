from abc import ABC, abstractmethod
from typing import Self

from notionary.user.client import UserHttpClient
from notionary.user.schemas import UserResponseDto, UserType
from notionary.utils.fuzzy import find_best_match


class BaseUser(ABC):
    def __init__(
        self,
        id: str,
        name: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._avatar_url = avatar_url

    @classmethod
    async def from_id(
        cls,
        user_id: str,
        http_client: UserHttpClient | None = None,
    ) -> Self:
        client = http_client or UserHttpClient()
        user_dto = await client.get_user_by_id(user_id)

        expected_type = cls._get_expected_user_type()
        if user_dto.type != expected_type:
            raise ValueError(f"User {user_id} is not a '{expected_type.value}', but '{user_dto.type.value}'")

        return cls.from_dto(user_dto)

    @classmethod
    async def from_name(
        cls,
        name: str,
        http_client: UserHttpClient | None = None,
    ) -> Self:
        client = http_client or UserHttpClient()
        all_users = await cls._get_all_users_of_type(client)

        if not all_users:
            user_type = cls._get_expected_user_type().value
            raise ValueError(f"No '{user_type}' users found in the workspace")

        best_match = find_best_match(query=name, items=all_users, text_extractor=cls._get_name_extractor())
        if not best_match:
            user_type = cls._get_expected_user_type().value
            raise ValueError(f"No '{user_type}' user found with name similar to '{name}'")

        return best_match

    @classmethod
    async def _get_all_users_of_type(cls, http_client: UserHttpClient) -> list[Self]:
        all_workspace_user_dtos = await http_client.get_all_workspace_users()
        expected_type = cls._get_expected_user_type()
        filtered_dtos = [dto for dto in all_workspace_user_dtos if dto.type == expected_type]
        return [cls.from_dto(dto) for dto in filtered_dtos]

    @classmethod
    @abstractmethod
    def _get_expected_user_type(cls) -> UserType:
        pass

    @classmethod
    @abstractmethod
    def from_dto(cls, user_dto: UserResponseDto) -> Self:
        pass

    @classmethod
    def _get_name_extractor(cls):
        return lambda user: user.name or ""

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def avatar_url(self) -> str | None:
        return self._avatar_url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r}, name={self._name!r})"
