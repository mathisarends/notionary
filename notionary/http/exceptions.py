class NotionApiError(Exception):
    """Base exception for Notion API errors"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_text: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class NotionAuthenticationError(NotionApiError):
    """Raised when authentication fails (401, 403)"""

    pass


class NotionPermissionError(NotionApiError):
    """Raised when access is denied due to insufficient permissions"""

    pass


class NotionRateLimitError(NotionApiError):
    """Raised when rate limit is exceeded (429)"""

    pass


class NotionResourceNotFoundError(NotionApiError):
    """Raised when a resource is not found (404)"""

    pass


class NotionValidationError(NotionApiError):
    """Raised when request validation fails (400)"""

    pass


class NotionServerError(NotionApiError):
    """Raised when server error occurs (5xx)"""

    pass


class NotionConnectionError(NotionApiError):
    """Raised when connection to Notion API fails"""

    pass
