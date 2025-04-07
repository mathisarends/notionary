class NotionDatabaseException(Exception):
    """Base exception for all Notion database operations."""
    pass


class DatabaseNotFoundException(NotionDatabaseException):
    """Exception raised when a database is not found."""
    
    def __init__(self, identifier: str, message: str = None):
        self.identifier = identifier
        self.message = message or f"Database not found: {identifier}"
        super().__init__(self.message)


class DatabaseInitializationError(NotionDatabaseException):
    """Exception raised when a database manager fails to initialize."""
    
    def __init__(self, database_id: str, message: str = None):
        self.database_id = database_id
        self.message = message or f"Failed to initialize database manager for ID: {database_id}"
        super().__init__(self.message)


class DatabaseConnectionError(NotionDatabaseException):
    """Exception raised when there's an error connecting to Notion API."""
    
    def __init__(self, message: str = None):
        self.message = message or "Error connecting to Notion API"
        super().__init__(self.message)


class DatabaseParsingError(NotionDatabaseException):
    """Exception raised when there's an error parsing database data."""
    
    def __init__(self, message: str = None):
        self.message = message or "Error parsing database data"
        super().__init__(self.message)