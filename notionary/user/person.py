from typing import Self, cast

from notionary.user.base import BaseUser
from notionary.user.schemas import PersonUserResponseDto, UserResponseDto, UserType


class PersonUser(BaseUser):
    def __init__(
        self,
        id: str,
        name: str,
        avatar_url: str,
        email: str,
    ) -> None:
        super().__init__(id=id, name=name, avatar_url=avatar_url)
        self._email = email

    @classmethod
    def _get_expected_user_type(cls) -> UserType:
        return UserType.PERSON

    @classmethod
    def from_dto(cls, user_dto: UserResponseDto) -> Self:
        person_dto = cast(PersonUserResponseDto, user_dto)
        return cls(
            id=person_dto.id,
            name=person_dto.name or "",
            avatar_url=person_dto.avatar_url,
            email=person_dto.person.email or "",
        )

    @property
    def name(self) -> str:
        return self._name or ""

    @property
    def email(self) -> str:
        return self._email

    def __repr__(self) -> str:
        return (
            f"PersonUser(id={self._id!r}, name={self._name!r}, email={self._email!r})"
        )
