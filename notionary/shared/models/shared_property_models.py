from __future__ import annotations

from enum import StrEnum


class PropertyType(StrEnum):
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
