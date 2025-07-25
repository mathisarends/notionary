class NotionDatabaseException(Exception):
    """Base exception for all Notion database operations."""

    pass


class DatabaseNotFoundException(NotionDatabaseException):
    """Exception raised when a database is not found."""

    def __init__(self, identifier: str, message: str = None):
        self.identifier = identifier
        self.message = message or f"Database not found: {identifier}"
        super().__init__(self.message)
