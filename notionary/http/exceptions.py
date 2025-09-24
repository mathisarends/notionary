class NotionApiError(Exception):
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
    pass


class NotionPermissionError(NotionApiError):
    pass


class NotionRateLimitError(NotionApiError):
    pass


class NotionResourceNotFoundError(NotionApiError):
    pass


class NotionValidationError(NotionApiError):
    pass


class NotionServerError(NotionApiError):
    pass


class NotionConnectionError(NotionApiError):
    pass
