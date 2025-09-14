from __future__ import annotations
from enum import StrEnum


class PropertyType(StrEnum):
    """Canonical Notion property types used across schema + page models."""

    SELECT = "select"
    MULTI_SELECT = "multi_select"
    STATUS = "status"
    RELATION = "relation"
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    PEOPLE = "people"
    CREATED_TIME = "created_time"


class NotionColor(StrEnum):
    """Known Notion color tokens (status/select/rich_text may reference these)."""

    DEFAULT = "default"
    GRAY = "gray"
    BROWN = "brown"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    PINK = "pink"
