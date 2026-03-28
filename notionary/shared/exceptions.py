from notionary.exceptions.base import NotionaryException


class EntityNotFound(NotionaryException):
    def __init__(
        self, entity_type: str, query: str, available_titles: list[str] | None = None
    ) -> None:
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
