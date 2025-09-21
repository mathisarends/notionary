from __future__ import annotations

from abc import ABC

from notionary.user.user_http_client import UserHttpClient
from notionary.util import LoggingMixin


class BaseNotionUser(LoggingMixin, ABC):
    """
    Base class for all Notion user types with common functionality.
    """

    def __init__(
        self,
        user_id: str,
        name: str | None = None,
        avatar_url: str | None = None,
        token: str | None = None,
    ):
        """Initialize base user properties."""
        self._user_id = user_id
        self._name = name
        self._avatar_url = avatar_url
        self.client = UserHttpClient(token=token)

    @property
    def id(self) -> str:
        """Get the user ID."""
        return self._user_id

    @property
    def name(self) -> str | None:
        """Get the user name."""
        return self._name

    @property
    def avatar_url(self) -> str | None:
        """Get the avatar URL."""
        return self._avatar_url

    def get_display_name(self) -> str:
        """Get a display name for the user."""
        return self._name or f"User {self._user_id[:8]}"

    def __str__(self) -> str:
        """String representation of the user."""
        return f"{self.__class__.__name__}(name='{self.get_display_name()}', id='{self._user_id[:8]}...')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()
