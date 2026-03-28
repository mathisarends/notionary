from notionary.shared.exceptions import EntityNotFound


class DatabaseNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("database", query, available_titles)
