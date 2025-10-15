from notionary.exceptions.base import NotionaryError


class EntityNotFound(NotionaryError):
    def __init__(self, entity_type: str, query: str, available_titles: list[str] | None = None) -> None:
        self.entity_type = entity_type
        self.query = query
        self.available_titles = available_titles or []

        if self.available_titles:
            message = (
                f"No sufficiently similar {entity_type} found for query '{query}'. "
                f"Did you mean one of these? Top results: {self.available_titles}"
            )
        else:
            message = f"No {entity_type} found for query '{query}'. The search returned no results."

        super().__init__(message)


class PageNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("page", query, available_titles)


class DataSourceNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("data source", query, available_titles)


class DatabaseNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("database", query, available_titles)


class NoUsersInWorkspace(NotionaryError):
    def __init__(self, user_type: str) -> None:
        self.user_type = user_type
        message = f"No '{user_type}' users found in the workspace."
        super().__init__(message)


class UserNotFound(NotionaryError):
    def __init__(self, user_type: str, query: str, available_names: list[str] | None = None) -> None:
        self.user_type = user_type
        self.query = query
        self.available_names = available_names or []

        if self.available_names:
            message = (
                f"No '{user_type}' user found with exact name '{query}'. "
                f"Did you mean one of these? {self.available_names}"
            )
        else:
            message = f"No '{user_type}' user found with name '{query}'."

        super().__init__(message)
