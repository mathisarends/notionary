from __future__ import annotations

from notionary.util import LoggingMixin


class NotionDataSource(LoggingMixin):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        last_edited_time: str,
        url: str,
        public_url: str | None = None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
        properties: dict | None = None,
    ) -> None:
        self._id = id
        self._title = title
        self._created_time = created_time
        self._last_edited_time = last_edited_time
        self._url = url
        self._public_url = public_url
        self._emoji_icon = emoji_icon
        self._external_icon_url = external_icon_url
        self._cover_image_url = cover_image_url
        self._description = description
        self._properties = properties or {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def created_time(self) -> str:
        return self._created_time

    @property
    def last_edited_time(self) -> str:
        return self._last_edited_time

    @property
    def url(self) -> str:
        return self._url

    @property
    def public_url(self) -> str | None:
        return self._public_url

    @property
    def emoji_icon(self) -> str | None:
        return self._emoji_icon

    @property
    def external_icon_url(self) -> str | None:
        return self._external_icon_url

    @property
    def cover_image_url(self) -> str | None:
        return self._cover_image_url

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def properties(self) -> dict:
        return self._properties

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"title={self._title!r}, "
            f"created_time={self._created_time!r}, "
            f"last_edited_time={self._last_edited_time!r}, "
            f"url={self._url!r}, "
            f"public_url={self._public_url!r}, "
            f"emoji_icon={self._emoji_icon!r}, "
            f"external_icon_url={self._external_icon_url!r}, "
            f"cover_image_url={self._cover_image_url!r}, "
            f"description={self._description!r}"
            f")"
        )
