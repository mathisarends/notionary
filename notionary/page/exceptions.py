from notionary.shared.exceptions import EntityNotFound


class PageNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("page", query, available_titles)
