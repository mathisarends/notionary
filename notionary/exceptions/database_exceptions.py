from typing import Optional


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
        
        
class PageNotFoundException(NotionDatabaseException):
    """Raised when a page is not found or cannot be accessed."""
    
    def __init__(self, page_id: str, message: Optional[str] = None):
        self.page_id = page_id
        self.message = message or f"Page not found: {page_id}"
        super().__init__(self.message)


class PageOperationError(NotionDatabaseException):
    """Raised when an operation on a page fails."""
    
    def __init__(self, page_id: str, operation: str, message: Optional[str] = None):
        self.page_id = page_id
        self.operation = operation
        self.message = message or f"Failed to {operation} page {page_id}"
        super().__init__(self.message)


class PropertyError(NotionDatabaseException):
    """Raised when there's an error with database properties."""
    
    def __init__(self, property_name: Optional[str] = None, message: Optional[str] = None):
        self.property_name = property_name
        self.message = message or f"Error with property{' ' + property_name if property_name else ''}"
        super().__init__(self.message)