from notionary.shared.exceptions import EntityNotFound


class DataSourceNotFound(EntityNotFound):
    def __init__(self, query: str, available_titles: list[str] | None = None) -> None:
        super().__init__("data source", query, available_titles)
