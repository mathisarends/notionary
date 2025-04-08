from typing import Optional


class PageCreationException(Exception):
    """Exception raised when page creation in Notion fails."""

    def __init__(self, message: str, response: Optional[dict] = None):
        super().__init__(message)
        self.response = response
