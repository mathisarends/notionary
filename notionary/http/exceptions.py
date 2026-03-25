class NotionError(Exception):
    pass


class NotionAuthenticationError(NotionError):
    pass


class NotionPermissionError(NotionError):
    pass


class NotionNotFoundError(NotionError):
    pass


class NotionValidationError(NotionError):
    pass


class NotionRateLimitError(NotionError):
    pass


class NotionServerError(NotionError):
    pass


class NotionConnectionError(NotionError):
    pass
