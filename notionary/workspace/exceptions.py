from notionary.shared.exceptions import EntityNotFound


class ResourceNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("resource", query, available_titles)
