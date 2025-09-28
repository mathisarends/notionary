from __future__ import annotations

from notionary.user.base_notion_user import BaseNotionUser
from notionary.user.models import NotionUserResponse
from notionary.user.user_http_client import UserHttpClient
from notionary.util import factory_only


class NotionUser(BaseNotionUser):
    NO_USERS_FOUND_MSG = "No users found in workspace"
    NO_PERSON_USERS_FOUND_MSG = "No person users found in workspace"

    @factory_only("from_user_id", "from_user_response", "from_name")
    def __init__(
        self,
        user_id: str,
        name: str | None = None,
        avatar_url: str | None = None,
        email: str | None = None,
    ):
        """Initialize person user with person-specific properties."""
        super().__init__(user_id, name, avatar_url)
        self._email = email

    @classmethod
    async def from_user_id(cls, user_id: str) -> NotionUser | None:
        client = UserHttpClient()
        user_response = await client.get_user(user_id)

        if user_response is None:
            cls.logger.error("Failed to load user data for ID: %s", user_id)
            return None

        # Ensure this is actually a person user
        if user_response.type != "person":
            cls.logger.error("User %s is not a person user (type: %s)", user_id, user_response.type)
            return None

        return cls._create_from_response(user_response)

    @classmethod
    async def from_name(cls, name: str, min_similarity: float = 0.6) -> NotionUser | None:
        from notionary.util.fuzzy import find_best_match

        client = UserHttpClient()

        try:
            # Get all users from workspace
            all_users_response = await client.get_all_users()

            if not all_users_response:
                cls.logger.warning(cls.NO_USERS_FOUND_MSG)
                raise ValueError(cls.NO_USERS_FOUND_MSG)

            person_users = [user for user in all_users_response if user.type == "person" and user.name]

            if not person_users:
                cls.logger.warning(cls.NO_PERSON_USERS_FOUND_MSG)
                raise ValueError(cls.NO_PERSON_USERS_FOUND_MSG)

            cls.logger.debug(
                "Found %d person users for fuzzy matching: %s",
                len(person_users),
                [user.name for user in person_users[:5]],
            )

            # Use fuzzy matching to find best match
            best_match = find_best_match(
                query=name,
                items=person_users,
                text_extractor=lambda user: user.name or "",
                min_similarity=min_similarity,
            )

            if not best_match:
                available_names = [user.name for user in person_users[:5]]
                cls.logger.warning(
                    "No sufficiently similar person user found for '%s' (min: %.3f). Available: %s",
                    name,
                    min_similarity,
                    available_names,
                )
                raise ValueError(f"No sufficiently similar person user found for '{name}'")

            cls.logger.info(
                "Found best match: '%s' with similarity %.3f for query '%s'",
                best_match.matched_text,
                best_match.similarity,
                name,
            )

            # Create NotionUser from the matched user response
            return cls._create_from_response(best_match.item)

        except Exception as e:
            cls.logger.error("Error finding user by name '%s': %s", name, str(e))
            raise

    @classmethod
    def from_user_response(cls, user_response: NotionUserResponse) -> NotionUser:
        if user_response.type != "person":
            raise ValueError(f"Cannot create NotionUser from {user_response.type} user")

        return cls._create_from_response(user_response)

    @property
    def email(self) -> str | None:
        return self._email

    @property
    def user_type(self) -> str:
        return "person"

    @property
    def is_person(self) -> bool:
        return True

    @property
    def is_bot(self) -> bool:
        return False

    @classmethod
    def _create_from_response(cls, user_response: NotionUserResponse) -> NotionUser:
        """Create NotionUser instance from API response."""
        email = user_response.person.email if user_response.person else None

        instance = cls(
            user_id=user_response.id,
            name=user_response.name,
            avatar_url=user_response.avatar_url,
            email=email,
        )

        cls.logger.info(
            "Created person user: '%s' (ID: %s)",
            user_response.name or "Unknown",
            user_response.id,
        )

        return instance
