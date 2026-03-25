from notionary.exceptions.base import NotionaryException


class NoUsersInWorkspace(NotionaryException):
    def __init__(self, user_type: str) -> None:
        self.user_type = user_type
        message = f"No '{user_type}' users found in the workspace."
        super().__init__(message)


class UserNotFound(NotionaryException):
    def __init__(
        self, user_type: str, query: str, available_names: list[str] | None = None
    ) -> None:
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
